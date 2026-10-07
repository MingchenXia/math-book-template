#!/usr/bin/env python3
"""Book workflow, using only Python's standard library. See docs/workflow.md."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ID = re.compile(r"OP-[A-Z0-9]+(?:-[A-Z0-9]+)*\Z")
RESULT = re.compile(r"\\begin\{(theorem|proposition|lemma|corollary)\}")
COVERAGE = {"statement", "proof", "dependencies", "sources", "second_pass"}


def fail(message):
    raise ValueError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as f:
        f.write(content)
        temporary = Path(f.name)
    temporary.replace(path)


def write_json(path, value):
    write(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def inside(base, relative):
    path = (base / relative).resolve()
    if not path.is_relative_to(base.resolve()):
        fail(f"Path escapes {base}: {relative}")
    return path


def run(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def config():
    value = read_json(ROOT / "bookflow.json")
    if value["phase"] not in {"draft", "revision"}:
        fail("phase must be draft or revision")
    if value["engine"] not in {"pdflatex", "xelatex", "lualatex"}:
        fail("Unsupported TeX engine")
    if value["bibliography_backend"] not in {"bibtex", "biber"}:
        fail("bibliography_backend must be bibtex or biber")
    if not re.fullmatch(r"[A-Za-z0-9_.-]+\.bib", Path(value["bibliography"]).name):
        fail("Use a bibliography filename containing letters, digits, dots, underscores or hyphens")
    return value


def uncomment(text):
    return re.sub(r"(?<!\\)%[^\n]*", "", text)


def argument(text, start):
    while start < len(text) and text[start].isspace():
        start += 1
    if start == len(text) or text[start] != "{":
        fail("BookProblem needs three braced arguments")
    depth, pos = 1, start + 1
    while pos < len(text):
        if text[pos] == "\\":
            pos += 2
            continue
        if text[pos] == "{":
            depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1:pos], pos + 1
        pos += 1
    fail("Unbalanced BookProblem argument")


def sources():
    """Follow static inputs in TeX reading order, relative to the book root."""
    entry = inside(ROOT, config()["root_tex"])
    book_dir = entry.parent
    ordered, active, seen = [], set(), set()

    def visit(path):
        if path in active:
            fail(f"Cyclic TeX input: {path}")
        if path in seen:
            fail(f"Repeated TeX input: {path}")
        if not path.is_file():
            fail(f"Missing TeX input: {path}")
        seen.add(path)
        active.add(path)
        ordered.append(path)
        body = uncomment(path.read_text(encoding="utf-8"))
        inputs = list(re.finditer(r"\\(?:input|include)\s*\{([^{}]+)\}", body))
        if len(inputs) != len(re.findall(r"\\(?:input|include)\b", body)):
            fail(f"Use static braced input paths in {path}")
        for match in inputs:
            name = match[1]
            if name.startswith("generated/"):
                continue
            if "\\" in name or "#" in name:
                fail(f"Dynamic TeX input is unsupported: {name}")
            child = inside(book_dir, name if Path(name).suffix else name + ".tex")
            visit(child)
        active.remove(path)

    visit(entry)
    return ordered


def problems():
    records = {}
    for path in sources():
        body = uncomment(path.read_text(encoding="utf-8"))
        for match in re.finditer(r"\\BookProblem\s*(?=\{)", body):
            problem_id, pos = argument(body, match.end())
            title, pos = argument(body, pos)
            statement, _ = argument(body, pos)
            if not ID.fullmatch(problem_id) or problem_id in records:
                fail(f"Invalid or duplicate problem ID: {problem_id}")
            records[problem_id] = {
                "id": problem_id, "title": title.strip(), "statement_tex": statement.strip(),
                "source": path.relative_to(ROOT).as_posix(),
                "line": body[:match.start()].count("\n") + 1,
            }
    return records


def digest(files, extra=None):
    contents = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    serialized = json.dumps({"files": contents, "extra": extra}, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serialized.encode()).hexdigest()


def review_inputs():
    inputs = sources() + [inside(ROOT, config()["bibliography"])]
    book = inside(ROOT, config()["root_tex"]).parent
    root_pdf = inside(ROOT, config()["root_tex"]).with_suffix(".pdf")
    asset_types = {".sty", ".cls", ".bst", ".ist", ".png", ".jpg", ".jpeg", ".pdf", ".eps", ".svg", ".otf", ".ttf"}
    inputs += [p for p in book.rglob("*") if p.is_file() and p.suffix.lower() in asset_types and "generated" not in p.relative_to(book).parts and p != root_pdf]
    if (book / "latexmkrc").exists():
        inputs.append(book / "latexmkrc")
    for folder in (ROOT / "references/papers", ROOT / "references/notes"):
        inputs += [p for p in folder.rglob("*") if p.is_file() and p.name != ".DS_Store"]
    return sorted(set(inputs))


def book_digest():
    files = review_inputs()
    files += sorted((ROOT / "research/solutions").glob("*/solution.json"))
    for meta_path in sorted((ROOT / "research/solutions").glob("*/solution.json")):
        files.append(inside(meta_path.parent, read_json(meta_path)["tex_file"]))
    # Settings affect the rendered text; phase and baseline bookkeeping do not.
    settings = {k: config()[k] for k in ("title", "author", "engine", "root_tex", "bibliography", "bibliography_backend")}
    settings["integrated_solutions"] = [r["id"] for r in catalogue() if r["integrated"]]
    return digest(files, settings)


def solution(problem_id, records):
    if problem_id not in records:
        fail(f"Unknown problem: {problem_id}")
    folder = ROOT / "research/solutions" / problem_id
    meta_path = folder / "solution.json"
    if not meta_path.exists():
        return None
    meta = read_json(meta_path)
    if meta.get("problem_id") != problem_id or meta.get("scope") not in {"full", "partial"}:
        fail(f"Invalid solution metadata: {meta_path}")
    tex = inside(folder, meta["tex_file"])
    body = uncomment(tex.read_text(encoding="utf-8"))
    if not RESULT.search(body) or "\\begin{proof}" not in body:
        fail(f"Solution needs a semantic result and proof: {tex}")
    if re.search(r"\\(?:input|include|write18|openout)\b", body):
        fail(f"Solution must be self-contained TeX: {tex}")
    if "\\BookProblem" in body:
        fail("Put residual questions in a chapter, not inside a solution")
    stamp = digest(review_inputs() + [meta_path, tex], records[problem_id])
    return meta, tex, stamp


def valid_review(report, expected, scope, problem_id=None, unit=None):
    if report.get("kind") != scope or report.get("problem_id") != problem_id:
        return False
    if report.get("unit") != unit:
        return False
    if report.get("source_sha256") != expected or report.get("verdict") != "approved":
        return False
    if not report.get("reviewer") or not COVERAGE.issubset(report.get("coverage", [])):
        return False
    if any(f.get("severity") in {"blocking", "major"} for f in report.get("findings", [])):
        return False
    return bool(report.get("summary"))


def branch():
    result = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def integration_allowed(problem_id):
    cfg = config()
    return cfg["phase"] == "draft" or problem_id in cfg["baseline_solutions"] or branch().startswith("revision/")


def catalogue():
    records = problems()
    for folder in (ROOT / "research/solutions").iterdir():
        if folder.is_dir() and (folder / "solution.json").exists() and folder.name not in records:
            fail(f"Orphan solution: {folder.name}; keep its original BookProblem in the source")
    for problem_id, record in records.items():
        item = solution(problem_id, records)
        record.update(status="open", integrated=False)
        if item is None:
            continue
        meta, tex, stamp = item
        review_path = ROOT / "research/reviews" / f"solution-{problem_id}.json"
        report = read_json(review_path) if review_path.exists() else {}
        record.update(solution=tex.relative_to(ROOT).as_posix(), source_sha256=stamp, scope=meta["scope"])
        if valid_review(report, stamp, "solution", problem_id):
            if meta["scope"] == "partial":
                record["status"] = "partial"
            else:
                record["integrated"] = integration_allowed(problem_id)
                record["status"] = "resolved" if record["integrated"] else "verified_pending_revision"
        elif report.get("source_sha256") and report["source_sha256"] != stamp:
            record["status"] = "review_stale"
        elif report.get("verdict") in {"needs_work", "rejected"}:
            record["status"] = report["verdict"]
        else:
            record["status"] = "candidate"
    return list(records.values())


def tex_escape(value):
    mapping = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}
    return "".join(mapping.get(c, c) for c in value)


def sync(check=False):
    records = catalogue()
    summary = {"problems": records, "counts": {s: sum(r["status"] == s for r in records) for s in sorted({r["status"] for r in records})}}
    markdown = "# 问题目录\n\n自动生成；编辑书稿中的 `\\BookProblem`，不要手改此文件。`open` 表示本书尚未解决，不等于已核实的文献开放问题。\n\n"
    for r in records:
        location = "../" + r["source"]
        title = r["title"].replace("\n", " ")
        markdown += f"## {r['id']} — {title}\n\n状态：`{r['status']}` · [书稿位置]({location})（源码第 {r['line']} 行）\n\n{r['statement_tex']}\n\n"
        if r.get("solution"):
            markdown += f"[解答](../{r['solution']}) · 审校指纹：`{r['source_sha256']}`\n\n"
    payloads = {
        ROOT / "research/open-problems.json": json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        ROOT / "research/open-problems.md": markdown.rstrip() + "\n",
    }
    if check:
        stale = [str(p.relative_to(ROOT)) for p, v in payloads.items() if not p.exists() or p.read_text(encoding="utf-8") != v]
        if stale:
            fail("Stale problem catalogue: " + ", ".join(stale) + "; run make sync")
        return
    for p, v in payloads.items():
        write(p, v)
    generated = ROOT / "book/generated"
    accepted = {r["id"] for r in records if r["integrated"]}
    for old in (generated / "solutions").glob("*.tex"):
        if old.stem not in accepted:
            old.unlink()
    status = "% Generated by bookflow; do not edit.\n"
    for r in records:
        if not r["integrated"]:
            continue
        status += f"\\expandafter\\def\\csname bfresolved@{r['id']}\\endcsname{{1}}\n"
        body = (ROOT / r["solution"]).read_text(encoding="utf-8")
        if f"\\label{{prob:{r['id']}}}" not in body:
            body = RESULT.sub(lambda m: m[0] + f"\\label{{prob:{r['id']}}}", body, count=1)
        write(generated / "solutions" / f"{r['id']}.tex", "% Generated from the reviewed solution.\n" + body)
    write(generated / "status.tex", status)
    cfg = config()
    bibliography_name = Path(cfg["bibliography"]).name
    write(generated / "metadata.tex", f"\\PassOptionsToPackage{{backend={cfg['bibliography_backend']}}}{{biblatex}}\n\\newcommand{{\\BookBibliography}}{{\\detokenize{{{bibliography_name}}}}}\n\\title{{{tex_escape(cfg['title'])}}}\n\\author{{{tex_escape(cfg['author'])}}}\n\\date{{}}\n")
    print("Problem catalogue:", summary["counts"])


def audit():
    records = catalogue()
    bodies = [uncomment(p.read_text(encoding="utf-8")) for p in sources()]
    bodies += [uncomment((ROOT / r["solution"]).read_text(encoding="utf-8")) for r in records if r["integrated"]]
    labels = [label for body in bodies for label in re.findall(r"\\label\{([^{}]+)\}", body) if "#" not in label]
    duplicates = {label for label in labels if labels.count(label) > 1}
    if duplicates:
        fail("Duplicate labels: " + ", ".join(sorted(duplicates)))
    available = set(labels) | {"prob:" + r["id"] for r in records}
    cited = set()
    for body in bodies:
        for refs in re.findall(r"\\(?:ref|eqref|cref|Cref|pageref)\{([^{}]+)\}", body):
            for label in refs.split(","):
                if label.strip() not in available:
                    fail(f"Unknown cross-reference: {label}")
        for keys in re.findall(r"\\[A-Za-z]*cite[A-Za-z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}", body):
            cited.update(k.strip() for k in keys.split(","))
    bib = inside(ROOT, config()["bibliography"]).read_text(encoding="utf-8")
    entries = re.findall(r"@(?!(?:comment|string|preamble)\b)[A-Za-z]+\s*\{\s*([^,\s]+)\s*,", bib, re.I)
    if len(entries) != len(set(entries)):
        fail("Duplicate bibliography keys")
    missing = cited - set(entries)
    if missing:
        fail("Unknown bibliography keys: " + ", ".join(sorted(missing)))
    print("Static labels and bibliography checks passed; this is not a proof review.")


def build():
    sync()
    audit()
    cfg = config()
    backend = cfg["bibliography_backend"]
    if not shutil.which("latexmk") or not shutil.which(backend):
        fail(f"Install the dev container or a TeX distribution with latexmk and {backend}")
    probe = subprocess.run([backend, "--version"], capture_output=True)
    if probe.returncode:
        fail(f"{backend} cannot run on this machine; use the container or another supported backend")
    source = inside(ROOT, cfg["root_tex"])
    output = ROOT / "build/pdf"
    signature = {k: cfg[k] for k in ("engine", "bibliography_backend", "root_tex")}
    signature["build_strategy"] = "local-output-directory-v1"
    signature_path = ROOT / "build/toolchain.json"
    if output.exists() and (not signature_path.exists() or read_json(signature_path) != signature):
        shutil.rmtree(output)  # Only this workflow's dedicated generated output directory.
    output.mkdir(parents=True, exist_ok=True)
    write_json(signature_path, signature)
    mode = {"pdflatex": "-pdf", "xelatex": "-xelatex", "lualatex": "-lualatex"}[cfg["engine"]]
    environment = os.environ.copy()
    environment["TEXINPUTS"] = str(source.parent) + "//" + os.pathsep + environment.get("TEXINPUTS", "")
    environment["BIBINPUTS"] = str(inside(ROOT, cfg["bibliography"]).parent) + os.pathsep + str(source.parent) + os.pathsep + environment.get("BIBINPUTS", "")
    command = ["latexmk"]
    rc = source.parent / "latexmkrc"
    if rc.exists():
        command += ["-r", str(rc)]
    command += [mode, "-interaction=nonstopmode", "-halt-on-error", "-file-line-error", str(source)]
    run(command, cwd=output, env=environment)
    log = (output / (source.stem + ".log")).read_text(encoding="utf-8", errors="replace")
    if re.search(r"(?:There were undefined references|Citation .* undefined|Reference .* undefined|multiply defined|Please \(re\)run (?:Biber|BibTeX))", log):
        fail("Build contains unresolved references or bibliography warnings")
    manifest = {"source_sha256": book_digest(), "pdf_sha256": hashlib.sha256((output / (source.stem + ".pdf")).read_bytes()).hexdigest()}
    write_json(ROOT / "build/build-manifest.json", manifest)
    print("PDF:", output / (source.stem + ".pdf"))


def chapter_report_path(unit):
    code = hashlib.sha256(unit.encode()).hexdigest()[:16]
    return ROOT / "research/reviews" / f"chapter-{code}.json"


def book_review_complete():
    stamp = book_digest()
    report = ROOT / "research/reviews/book.json"
    if report.exists() and valid_review(read_json(report), stamp, "book"):
        return True
    for path in sources():
        unit = path.relative_to(ROOT).as_posix()
        report = chapter_report_path(unit)
        if not report.exists() or not valid_review(read_json(report), stamp, "chapter", unit=unit):
            return False
    return True


def page_range(value):
    numbers = set()
    for item in value.split(","):
        match = re.fullmatch(r"([1-9][0-9]*)(?:-([1-9][0-9]*))?", item)
        if not match:
            fail("Pages must be PDF physical page numbers, e.g. 3-5,8")
        first, last = int(match[1]), int(match[2] or match[1])
        if last < first or last > 100000:
            fail("Invalid PDF page range")
        numbers.update(range(first, last + 1))
    return sorted(numbers)


def review_previews(pages=None):
    pdf = ROOT / "build/pdf" / (Path(config()["root_tex"]).stem + ".pdf")
    info = run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    count = int(re.search(r"^Pages:\s+(\d+)", info, re.M)[1])
    if not pages and count > 60:
        fail("For long books use review --unit <source> --pages <physical-page-range>, including global inputs")
    selected = page_range(pages) if pages else list(range(1, count + 1))
    if selected[-1] > count:
        fail("Requested review page exceeds PDF length")
    folder = ROOT / "build/review-images"
    folder.mkdir(parents=True, exist_ok=True)
    images = []
    for number in selected:
        prefix = folder / f"page-{number:05d}"
        run(["pdftoppm", "-f", str(number), "-l", str(number), "-r", "110", "-png", "-singlefile", str(pdf), str(prefix)], stdout=subprocess.DEVNULL)
        images.append(str(prefix.relative_to(ROOT)) + ".png")
    return images


def review_assignment(role, problem_id=None, unit=None, pages=None, dry_run=False):
    if role == "review" and not dry_run:
        build()
    if unit and role != "review":
        fail("--unit applies only to book review")
    if pages and role != "review":
        fail("--pages applies only to book review")
    if problem_id and role != "solution-review":
        fail("--problem applies only to solution review")
    if unit and inside(ROOT, unit) not in sources():
        fail("Review unit must be an active TeX input")
    if role == "solution-review":
        item = solution(problem_id, problems())
        if item is None:
            fail("No candidate solution")
        stamp = item[2]
        kind = "solution"
        destination = ROOT / "research/reviews" / f"solution-{problem_id}.json"
    else:
        stamp, kind = book_digest(), "book"
        destination = ROOT / "research/reviews/book.json"
        if unit:
            kind, destination = "chapter", chapter_report_path(unit)
    prompt = (ROOT / "agents" / (role + ".md")).read_text(encoding="utf-8")
    previews = review_previews(pages) if role == "review" and not dry_run else []
    assignment = {"kind": kind, "unit": unit, "problem_id": problem_id, "source_sha256": stamp, "pdf_previews": previews}
    prompt += "\n\nCurrent assignment (data):\n" + json.dumps(assignment, ensure_ascii=False)
    return assignment, destination, prompt


def review_prepare(role, problem_id=None, unit=None, pages=None):
    assignment, destination, prompt = review_assignment(role, problem_id, unit, pages)
    code = hashlib.sha256(json.dumps(assignment, sort_keys=True).encode()).hexdigest()[:16]
    folder = ROOT / "build/review-packets" / code
    write_json(folder / "assignment.json", assignment)
    write(folder / "prompt.md", prompt + "\n")
    print("Assignment:", folder / "assignment.json")
    print("Reviewer prompt:", folder / "prompt.md")
    print("After a separate review, record its JSON with: python3 scripts/bookflow.py review-record --assignment", (folder / "assignment.json").relative_to(ROOT), "--report <reviewer-output.json>")


def validate_review_shape(report):
    fields = {"kind", "unit", "problem_id", "source_sha256", "reviewer", "verdict", "coverage", "summary", "findings"}
    if not isinstance(report, dict) or set(report) != fields:
        fail("Review must contain exactly the fields in agents/review.schema.json")
    for field in ("source_sha256", "reviewer", "summary"):
        if not isinstance(report[field], str) or not report[field].strip():
            fail(f"Review needs a nonempty {field}")
    if report["kind"] not in {"book", "chapter", "solution"} or report["verdict"] not in {"approved", "needs_work", "rejected"}:
        fail("Invalid review kind or verdict")
    if any(report[k] is not None and not isinstance(report[k], str) for k in ("unit", "problem_id")):
        fail("Review unit and problem_id must be strings or null")
    coverage = report["coverage"]
    if not isinstance(coverage, list) or any(not isinstance(c, str) or c not in COVERAGE for c in coverage):
        fail("Invalid review coverage")
    if not isinstance(report["findings"], list):
        fail("Review findings must be a list")
    for finding in report["findings"]:
        if not isinstance(finding, dict) or set(finding) != {"severity", "file", "line", "message", "suggestion"}:
            fail("Invalid review finding fields")
        if finding["severity"] not in {"blocking", "major", "minor"} or type(finding["line"]) is not int or finding["line"] < 1:
            fail("Invalid review finding severity or line")
        if any(not isinstance(finding[k], str) or not finding[k].strip() for k in ("file", "message", "suggestion")):
            fail("Review finding needs a file, message and suggestion")


def review_record(assignment_path, report_path):
    assignment = read_json(inside(ROOT, assignment_path))
    report = read_json(inside(ROOT, report_path))
    validate_review_shape(report)
    kind, problem_id, unit = (assignment.get(k) for k in ("kind", "problem_id", "unit"))
    stamp = assignment.get("source_sha256")
    if kind == "solution" and unit is None:
        item = solution(problem_id, problems())
        if item is None:
            fail("No candidate solution")
        current = item[2]
        destination = ROOT / "research/reviews" / f"solution-{problem_id}.json"
    elif kind in {"book", "chapter"} and problem_id is None:
        if (kind == "book" and unit is not None) or (kind == "chapter" and (not isinstance(unit, str) or inside(ROOT, unit) not in sources())):
            fail("Invalid book review unit")
        current = book_digest()
        destination = chapter_report_path(unit) if kind == "chapter" else ROOT / "research/reviews/book.json"
    else:
        fail("Invalid review assignment")
    if current != stamp:
        fail("Source changed during review; discard the report and rerun")
    if any(report.get(k) != assignment.get(k) for k in ("source_sha256", "kind", "problem_id", "unit")):
        fail("Review response does not match the assigned input")
    if report["verdict"] == "approved" and not valid_review(report, stamp, kind, problem_id, unit):
        fail("Incomplete approval report; all coverage areas and a second pass are required")
    write_json(destination, report)
    print("Review:", destination)
    sync()


def agent(role, problem_id=None, dry_run=False, unit=None, pages=None):
    cli_defaults = ["--ignore-user-config"] if os.environ.get("BOOKFLOW_CLI_DEFAULTS") == "1" else []
    if role == "edit" and config()["phase"] == "revision" and not branch().startswith("revision/"):
        fail("Start a revision branch before editing a completed book")
    assignment, destination, prompt = review_assignment(role, problem_id, unit, pages, dry_run)
    if role == "edit":
        command = ["codex", "exec", *cli_defaults, "--sandbox", "workspace-write", "--cd", str(ROOT), "-"]
        if dry_run:
            print(json.dumps(command)); print(prompt); return
        run(command, input=prompt, text=True, cwd=ROOT)
        sync()
        return
    command = ["codex", "exec", *cli_defaults, "--sandbox", "read-only", "--cd", str(ROOT), "--output-schema", str(ROOT / "agents/review.schema.json"), "--output-last-message"]
    if dry_run:
        print(json.dumps(command + [str(destination), "-"])); print(prompt); return
    if not shutil.which("codex"):
        fail("Codex CLI missing. Use the dev container or install @openai/codex; then codex login")
    # The CLI harness writes the final response; the reviewing agent has read-only tools.
    (ROOT / "build").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=ROOT / "build") as temp:
        response = Path(temp) / "review.json"
        assignment_file = Path(temp) / "assignment.json"
        write_json(assignment_file, assignment)
        run(command + [str(response), "-"], input=prompt, text=True, cwd=ROOT)
        review_record(assignment_file, response)


def finish():
    cfg = config()
    if cfg["phase"] != "draft":
        fail("Book is already in revision phase")
    if not book_review_complete():
        fail("A current approved full-book review is required before finish")
    build()
    baseline = read_json(ROOT / "build/build-manifest.json")
    cfg["baseline_solutions"] = [r["id"] for r in catalogue() if r["integrated"]]
    cfg["phase"] = "revision"
    write_json(ROOT / "research/editorial/baseline.json", baseline)
    write_json(ROOT / "bookflow.json", cfg)
    units = [p.relative_to(ROOT).as_posix() for p in sources()]
    write_json(ROOT / "research/editorial/revision-queue.json", {"units": [{"source": p, "status": "pending", "notes": ""} for p in units]})
    sync()
    print("Revision phase started. Commit the baseline; subsequent mathematical changes use revision branches and author-reviewed PRs.")


def revision_start(name):
    if config()["phase"] != "revision":
        fail("Run finish after the draft has passed a whole-book review")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        fail("Use a lowercase hyphenated revision name")
    status = run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout
    if status:
        fail("Commit or preserve existing work before starting a revision")
    if branch() != config()["main_branch"]:
        fail("Start from the synchronized main branch")
    run(["git", "switch", "-c", "revision/" + name], cwd=ROOT)


def revision_prepare(base, pages, summary):
    if config()["phase"] != "revision" or not branch().startswith("revision/"):
        fail("Prepare the proposal on a revision branch")
    if not book_review_complete():
        fail("Rerun the full-book review after the final revision")
    # Resolve the ref first; subprocess arguments never pass through a shell.
    base_sha = run(["git", "rev-parse", "--verify", base + "^{commit}"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    build()
    patch = run(["git", "diff", base_sha, "--", ".", ":(exclude)research/reviews/*"], cwd=ROOT, capture_output=True, text=True).stdout
    if not patch:
        fail("No changes to prepare")
    log_diff = run(["git", "diff", base_sha, "--", "CHANGELOG.md"], cwd=ROOT, capture_output=True, text=True).stdout
    if not log_diff:
        fail("Record the actual revision and checks in CHANGELOG.md before preparing the proposal")
    name = branch().split("/", 1)[1]
    write(ROOT / "build/revision" / (name + ".patch"), patch)
    page_numbers = page_range(pages)
    for tool in ("pdfseparate", "pdfunite"):
        if not shutil.which(tool):
            fail("Install Poppler for review PDF excerpts")
    pdf = ROOT / "build/pdf" / (Path(config()["root_tex"]).stem + ".pdf")
    excerpt = ROOT / "build/revision" / (name + "-excerpt.pdf")
    with tempfile.TemporaryDirectory(dir=ROOT / "build") as temp:
        parts = []
        for number in sorted(page_numbers):
            pattern = str(Path(temp) / "page-%d.pdf")
            run(["pdfseparate", "-f", str(number), "-l", str(number), str(pdf), pattern])
            parts.append(str(Path(temp) / f"page-{number}.pdf"))
        run(["pdfunite", *parts, str(excerpt)])
    manifest = {"branch": branch(), "base_sha": base_sha, "source_sha256": book_digest(), "pages": sorted(page_numbers), "summary": summary, "author_approval": "pending"}
    write_json(ROOT / "research/editorial/proposals" / (name + ".json"), manifest)
    write(ROOT / "build/revision" / (name + "-pr.md"), f"{summary}\n\nValidation: full source review and PDF compilation passed.\n\nSource fingerprint: `{manifest['source_sha256']}`\n\nReview PDF physical pages: {pages}. Download the matching book PDF from this PR's Book checks artifact; the local excerpt is `{excerpt.name}`. The author must inspect all changed passages, and explicitly approve this source fingerprint before merge or publication.\n")
    print("Prepared:", excerpt, "\nPR body:", ROOT / "build/revision" / (name + "-pr.md"))


def guard():
    if config()["phase"] != "revision" or branch().startswith("revision/"):
        return
    changes = run(["git", "diff", "--cached", "--name-only"], cwd=ROOT, capture_output=True, text=True).stdout.splitlines()
    if any(p.startswith(("book/", "research/solutions/", "references/")) for p in changes):
        fail("Completed-book source changes must be proposed on a revision/* branch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("sync"); p.add_argument("--check", action="store_true")
    for name in ("audit", "build", "finish", "guard"):
        sub.add_parser(name)
    p = sub.add_parser("agent"); p.add_argument("role", choices=["review", "solution-review", "edit"]); p.add_argument("--problem"); p.add_argument("--dry-run", action="store_true"); p.add_argument("--unit"); p.add_argument("--pages")
    p = sub.add_parser("review-prepare"); p.add_argument("role", choices=["review", "solution-review"]); p.add_argument("--problem"); p.add_argument("--unit"); p.add_argument("--pages")
    p = sub.add_parser("review-record"); p.add_argument("--assignment", required=True); p.add_argument("--report", required=True)
    p = sub.add_parser("revision-start"); p.add_argument("name")
    p = sub.add_parser("revision-prepare"); p.add_argument("--base", default="main"); p.add_argument("--pages", required=True); p.add_argument("--summary", required=True)
    args = parser.parse_args()
    try:
        if args.command == "sync": sync(args.check)
        elif args.command == "agent": agent(args.role, args.problem, args.dry_run, args.unit, args.pages)
        elif args.command == "review-prepare": review_prepare(args.role, args.problem, args.unit, args.pages)
        elif args.command == "review-record": review_record(args.assignment, args.report)
        elif args.command == "revision-start": revision_start(args.name)
        elif args.command == "revision-prepare": revision_prepare(args.base, args.pages, args.summary)
        else: globals()[args.command]()
    except (ValueError, KeyError, OSError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        print("bookflow:", error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
