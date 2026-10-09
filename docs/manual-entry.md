# Manually adding open problems and solutions

| What you want to do | Entry point | Files affected |
| --- | --- | --- |
| View the open problem list | [Current catalogue](../research/open-problems.md) | Read-only: stable IDs, status, manuscript locations and solution links |
| Add an open problem | `problem-add`, or insert the [problem template](templates/problem.tex) into an active chapter | The chapter's `BookProblem` and generated catalogue |
| Submit an existing full or partial answer | `solution-import`, or upload the [proof](templates/solution.tex) and [metadata](templates/solution.json) templates | `research/solutions/<ID>/`, awaiting independent review |
| Integrate an approved solution | Independent `solution-review` / `review-prepare`, registration of the actual report, then `make build` | Catalogue and generated text at the original question location |

You can give Codex a problem or answer and ask it to record it with these commands. Submission saves the mathematical content you provide. Describing an answer as solved does not create review approval.

## Add an open problem

1. Check the [catalogue](../research/open-problems.md) and choose an unused stable ID. Do not reuse resolved IDs.
2. Save the full statement as repository-local TeX, such as `work/statement.tex`. Include hypotheses, conclusion and scope. Use statement text and any needed formulas, without a `BookProblem`, document wrapper or chapter command.
3. Run from the repository root, replacing the example ID, title, file and target chapter:

```sh
python3 scripts/bookflow.py problem-add \
  --id OP-003 \
  --chapter book/chapters/02-questions.tex \
  --title 'New problem title' \
  --statement-file work/statement.tex
make check
make build
```

The command appends `BookProblem` to the active chapter and synchronizes the catalogue. It rejects duplicate IDs, inactive chapters, the root document, escaping paths and unbalanced braces. Check its reading position. If it belongs after a particular definition or result, move the complete macro there and run `make sync && make check && make build`. The command does not establish that the problem is open in the literature.

**Using GitHub's web editor:** edit the appropriate `book/chapters/*.tex` file, replace the placeholders in the [problem template](templates/problem.tex) and insert it at the appropriate location. Ask Codex or run `make sync` locally and commit the generated `research/open-problems.md/json` with the PR. Catalogue artifacts are not automatically written back to Git. Do not edit the generated list directly.

## Submit an existing solution

Find the stable ID and retain its original `BookProblem` in the chapter. Save the result and full proof as repository-local TeX, such as `work/answer.tex`. Use `proposition/theorem/lemma/corollary` and `proof` environments, without an entire document. See the [proof template](templates/solution.tex).

```sh
python3 scripts/bookflow.py solution-import \
  --problem OP-002 \
  --file work/answer.tex \
  --scope full \
  --dependency def:compactness
make check
make build
```

Use `--scope full` for an answer to the entire question, or `--scope partial` for a special case or partial conclusion. Repeat `--dependency label` for manuscript dependencies and `--reference bib-key` for references. Bibliography entries remain in `references/references.bib`. Recording those strings does not verify their content.

Import creates `research/solutions/OP-002/solution.tex` and `solution.json`, synchronizes the list and does not create an approved report. New submissions become candidate, not resolved. Existing folders are not overwritten by default. Edit the existing files directly or explicitly use `--replace` to import a replacement. First preserve any old draft you need in Git. Earlier reports are retained and become stale when relevant input changes.

**Using GitHub's web interface:** select **Add file → Create new file** to create `research/solutions/<ID>/solution.json`, following the [metadata template](templates/solution.json). Set the correct ID, scope, dependencies and references. Upload or create `solution.tex` in the same folder with your actual result and complete proof. Edit the existing folder when updating an answer. Submit both files and the synchronized catalogue in one PR. Do not invent review JSON or edit `book/generated/`. An existing review still applies when it remains valid for the current input; uploading a file does not create new approval.

## Review, integration and submission

With an authenticated CLI:

```sh
python3 scripts/bookflow.py agent solution-review --problem OP-002
make build
make review
```

With a hosted reviewer in Codex Cloud:

```sh
python3 scripts/bookflow.py review-prepare solution-review --problem OP-002
# Give the printed prompt to an independent read-only reviewer and preserve its actual JSON response.
python3 scripts/bookflow.py review-record \
  --assignment build/review-packets/<printed-fingerprint>/assignment.json \
  --report build/cloud-review.json
make build
```

See the [cloud guide](codex-cloud.md) for independent review and book checks. After a complete answer passes review for its current input, `make sync/build` incorporates the result and proof at the original question and sets status to resolved. Partial answers keep the full problem open. Check outdated claims elsewhere, affected consequences and reading order, inspect the PDF and complete the corresponding manuscript review.

Record actual changes and checks in `CHANGELOG.md`, update `research/STATUS.md`, and commit the affected chapter, solution folder, actual review report when available, and `research/open-problems.md/json` together. **Unreviewed candidates can be saved in the repository**, but must not be described as verified by the book. Temporary `work/` inputs and `build/` outputs need not be committed.

In the completed-book `phase=revision`, first run `python3 scripts/bookflow.py revision-start <proposal-name>`. Add problems or answers on that branch. Newly approved full solutions integrate only on `revision/*` proposals. The author must inspect the current PDF excerpts and explicitly approve before merge. See the [complete revision procedure](revision.md).
