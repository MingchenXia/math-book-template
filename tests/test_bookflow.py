import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("bookflow", REPO / "scripts/bookflow.py")
flow = importlib.util.module_from_spec(spec)
spec.loader.exec_module(flow)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        fixture = REPO / "tests/fixtures/demo"
        for name in ("book", "research", "references"):
            shutil.copytree(fixture / name, self.root / name, ignore=shutil.ignore_patterns("generated", "*.pdf", "__pycache__"))
        shutil.copy(fixture / "bookflow.json", self.root / "bookflow.json")
        # Tests always start from a draft without approvals, independent of the user's book.
        cfg = json.loads((self.root / "bookflow.json").read_text())
        cfg.update(phase="draft", baseline_solutions=[])
        (self.root / "bookflow.json").write_text(json.dumps(cfg))
        for p in (self.root / "research/reviews").glob("*.json"):
            p.unlink()
        self.root_patch = patch.object(flow, "ROOT", self.root)
        self.root_patch.start()
        self.branch_patch = patch.object(flow, "branch", return_value="main")
        self.branch_mock = self.branch_patch.start()

    def tearDown(self):
        self.branch_patch.stop()
        self.root_patch.stop()
        self.temp.cleanup()

    def approve(self, scope="full", coverage=None):
        meta_path = self.root / "research/solutions/OP-001/solution.json"
        meta = flow.read_json(meta_path)
        meta["scope"] = scope
        flow.write_json(meta_path, meta)
        stamp = flow.solution("OP-001", flow.problems())[2]
        flow.write_json(self.root / "research/reviews/solution-OP-001.json", {
            "kind": "solution", "problem_id": "OP-001", "source_sha256": stamp,
            "reviewer": "unit-test fixture", "verdict": "approved", "summary": "Test-only report",
            "coverage": list(flow.COVERAGE) if coverage is None else coverage, "findings": [],
        })

    def cloud_review(self, kind="solution", unit=None):
        problem_id = "OP-001" if kind == "solution" else None
        stamp = flow.solution(problem_id, flow.problems())[2] if problem_id else flow.book_digest()
        assignment = {"kind": kind, "unit": unit, "problem_id": problem_id, "source_sha256": stamp, "pdf_previews": []}
        report = {**{k: v for k, v in assignment.items() if k != "pdf_previews"},
                  "reviewer": "independent test fixture", "verdict": "approved", "coverage": sorted(flow.COVERAGE),
                  "summary": "Test-only report; not a mathematical approval", "findings": []}
        flow.write_json(self.root / "build/assignment.json", assignment)
        flow.write_json(self.root / "build/response.json", report)
        return assignment, report

    def test_cloud_full_review_integrates_current_solution(self):
        self.cloud_review()
        flow.review_record("build/assignment.json", "build/response.json")
        self.assertEqual(flow.catalogue()[0]["status"], "resolved")

    def test_cloud_partial_review_keeps_full_question_open(self):
        path = self.root / "research/solutions/OP-001/solution.json"
        meta = flow.read_json(path); meta["scope"] = "partial"; flow.write_json(path, meta)
        self.cloud_review()
        flow.review_record("build/assignment.json", "build/response.json")
        self.assertEqual(flow.catalogue()[0]["status"], "partial")

    def test_cloud_review_rejects_changed_source(self):
        self.cloud_review()
        proof = self.root / "research/solutions/OP-001/solution.tex"
        proof.write_text(proof.read_text() + "\n% Revised proof\n")
        with self.assertRaisesRegex(ValueError, "Source changed"):
            flow.review_record("build/assignment.json", "build/response.json")
        self.assertFalse((self.root / "research/reviews/solution-OP-001.json").exists())

    def test_cloud_review_rejects_different_assignment(self):
        _, report = self.cloud_review()
        report["problem_id"] = "OP-002"
        flow.write_json(self.root / "build/response.json", report)
        with self.assertRaisesRegex(ValueError, "does not match"):
            flow.review_record("build/assignment.json", "build/response.json")

    def test_cloud_review_rejects_incomplete_approval(self):
        _, report = self.cloud_review()
        report["coverage"].remove("second_pass")
        flow.write_json(self.root / "build/response.json", report)
        with self.assertRaisesRegex(ValueError, "Incomplete approval"):
            flow.review_record("build/assignment.json", "build/response.json")

    def test_cloud_review_rejects_unstructured_findings(self):
        _, report = self.cloud_review()
        report["findings"] = [{"severity": "minor", "message": "Missing file and locator"}]
        flow.write_json(self.root / "build/response.json", report)
        with self.assertRaisesRegex(ValueError, "finding fields"):
            flow.review_record("build/assignment.json", "build/response.json")

    def test_cloud_needs_work_is_saved_without_integration(self):
        _, report = self.cloud_review()
        report["verdict"] = "needs_work"
        report["coverage"] = ["statement"]
        report["findings"] = [{"severity": "major", "file": "research/solutions/OP-001/solution.tex", "line": 1,
                               "message": "Test-only gap", "suggestion": "Complete the proof"}]
        flow.write_json(self.root / "build/response.json", report)
        flow.review_record("build/assignment.json", "build/response.json")
        self.assertEqual(flow.catalogue()[0]["status"], "needs_work")
        self.assertFalse(flow.catalogue()[0]["integrated"])

    def test_cloud_chapter_review_records_only_assigned_active_input(self):
        unit = "book/chapters/01-foundations.tex"
        _, report = self.cloud_review("chapter", unit)
        flow.review_record("build/assignment.json", "build/response.json")
        self.assertEqual(flow.read_json(flow.chapter_report_path(unit)), report)
        self.assertFalse(flow.book_review_complete())

    def test_cloud_prepare_exports_exact_assignment_without_cli(self):
        shutil.copytree(REPO / "agents", self.root / "agents")
        with patch.object(flow, "run", side_effect=AssertionError("No CLI may execute")):
            flow.review_prepare("solution-review", "OP-001")
        assignment_path = next((self.root / "build/review-packets").glob("*/assignment.json"))
        assignment = flow.read_json(assignment_path)
        self.assertEqual(assignment["source_sha256"], flow.solution("OP-001", flow.problems())[2])
        self.assertIn(assignment["source_sha256"], (assignment_path.parent / "prompt.md").read_text())

    def test_cloud_review_cannot_read_report_outside_repository(self):
        self.cloud_review()
        with self.assertRaisesRegex(ValueError, "escapes"):
            flow.review_record("build/assignment.json", "../response.json")

    def test_unreviewed_answer_does_not_replace_question(self):
        flow.sync()
        self.assertEqual(flow.catalogue()[0]["status"], "candidate")
        self.assertFalse((self.root / "book/generated/solutions/OP-001.tex").exists())

    def test_full_approved_answer_is_integrated_and_keeps_label(self):
        self.approve()
        flow.sync()
        self.assertEqual(flow.catalogue()[0]["status"], "resolved")
        tex = (self.root / "book/generated/solutions/OP-001.tex").read_text()
        self.assertIn(r"\label{prob:OP-001}", tex)
        self.assertIn(r"\begin{proof}", tex)
        flow.audit()

    def test_partial_answer_keeps_full_question_open(self):
        self.approve(scope="partial")
        flow.sync()
        self.assertEqual(flow.catalogue()[0]["status"], "partial")
        self.assertFalse(flow.catalogue()[0]["integrated"])

    def test_incomplete_approval_is_not_accepted(self):
        self.approve(coverage=["statement", "proof"])
        self.assertEqual(flow.catalogue()[0]["status"], "candidate")

    def test_major_finding_overrides_approval(self):
        self.approve()
        p = self.root / "research/reviews/solution-OP-001.json"
        report = flow.read_json(p)
        report["findings"] = [{"severity": "major", "message": "Proof gap"}]
        flow.write_json(p, report)
        self.assertFalse(flow.catalogue()[0]["integrated"])

    def test_changed_proof_invalidates_review_and_removes_generated_proof(self):
        self.approve()
        flow.sync()
        p = self.root / "research/solutions/OP-001/solution.tex"
        p.write_text(p.read_text() + "\n% New candidate version\n")
        flow.sync()
        self.assertEqual(flow.catalogue()[0]["status"], "review_stale")
        self.assertFalse((self.root / "book/generated/solutions/OP-001.tex").exists())

    def test_changed_hypotheses_invalidate_review(self):
        self.approve()
        p = self.root / "book/chapters/02-questions.tex"
        p.write_text(p.read_text().replace("Fix a compact space", "Fix a locally compact space"))
        self.assertEqual(flow.catalogue()[0]["status"], "review_stale")

    def test_changed_binary_figure_invalidates_review(self):
        figure = self.root / "book/figures/diagram.png"
        figure.parent.mkdir()
        figure.write_bytes(b"first binary asset\x00")
        self.approve()
        figure.write_bytes(b"changed binary asset\x00")
        self.assertEqual(flow.catalogue()[0]["status"], "review_stale")

    def test_accepting_solution_invalidates_prior_whole_book_review(self):
        before = flow.book_digest()
        self.approve()
        self.assertNotEqual(before, flow.book_digest())

    def test_revision_main_defers_new_solutions(self):
        self.approve()
        cfg = flow.config(); cfg["phase"] = "revision"
        flow.write_json(self.root / "bookflow.json", cfg)
        self.assertEqual(flow.catalogue()[0]["status"], "verified_pending_revision")
        self.branch_mock.return_value = "revision/fix-boundedness"
        self.assertEqual(flow.catalogue()[0]["status"], "resolved")

    def test_revision_baseline_preserves_existing_solutions(self):
        self.approve()
        cfg = flow.config(); cfg.update(phase="revision", baseline_solutions=["OP-001"])
        flow.write_json(self.root / "bookflow.json", cfg)
        self.assertEqual(flow.catalogue()[0]["status"], "resolved")

    def test_duplicate_problem_id_is_rejected(self):
        p = self.root / "book/chapters/02-questions.tex"
        p.write_text(p.read_text() + r"\BookProblem{OP-001}{Duplicate}{Text}")
        with self.assertRaisesRegex(ValueError, "duplicate"):
            flow.problems()

    def test_nested_braces_and_comments_are_parsed(self):
        p = self.root / "book/chapters/02-questions.tex"
        p.write_text(p.read_text() + "\n% \\BookProblem{OP-999}{Hidden}{Ignore}\n" + r"\BookProblem{OP-003}{A title}{Is $\{x\in X : f(x)=0\}$ compact?}")
        records = flow.problems()
        self.assertNotIn("OP-999", records)
        self.assertIn(r"\{x\in X", records["OP-003"]["statement_tex"])

    def test_recursive_input_cycle_is_rejected(self):
        p = self.root / "book/chapters/01-foundations.tex"
        p.write_text(p.read_text() + "\n\\input{main}\n")
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            flow.sources()

    def test_missing_input_is_rejected(self):
        (self.root / "book/chapters/01-foundations.tex").unlink()
        with self.assertRaisesRegex(ValueError, "Missing"):
            flow.sources()

    def test_solution_path_escape_is_rejected(self):
        p = self.root / "research/solutions/OP-001/solution.json"
        meta = flow.read_json(p); meta["tex_file"] = "../../STATUS.md"
        flow.write_json(p, meta)
        with self.assertRaisesRegex(ValueError, "escapes"):
            flow.catalogue()

    def test_stale_catalogue_check_fails(self):
        flow.sync()
        (self.root / "research/open-problems.md").write_text("old list")
        with self.assertRaisesRegex(ValueError, "Stale"):
            flow.sync(check=True)

    def test_missing_reference_is_rejected(self):
        p = self.root / "book/chapters/01-foundations.tex"
        p.write_text(p.read_text() + r"See \cref{lem:missing}.")
        with self.assertRaisesRegex(ValueError, "Unknown cross-reference"):
            flow.audit()

    def test_finish_requires_current_full_review(self):
        with self.assertRaisesRegex(ValueError, "full-book review"):
            flow.finish()

    def test_chapter_reviews_require_all_inputs_at_same_fingerprint(self):
        stamp = flow.book_digest()
        for p in flow.sources():
            unit = p.relative_to(self.root).as_posix()
            flow.write_json(flow.chapter_report_path(unit), {
                "kind": "chapter", "unit": unit, "problem_id": None, "source_sha256": stamp,
                "reviewer": "test fixture", "verdict": "approved", "coverage": list(flow.COVERAGE),
                "summary": "Test-only scoped review", "findings": [],
            })
        self.assertTrue(flow.book_review_complete())
        first = flow.sources()[0]
        first.write_text(first.read_text() + "\n% New source version\n")
        self.assertFalse(flow.book_review_complete())

    def test_finish_preserves_resolutions_and_creates_complete_revision_queue(self):
        self.approve()
        stamp = flow.book_digest()
        flow.write_json(self.root / "research/reviews/book.json", {
            "kind": "book", "unit": None, "problem_id": None, "source_sha256": stamp,
            "reviewer": "test fixture", "verdict": "approved", "coverage": list(flow.COVERAGE),
            "summary": "Test-only full review", "findings": [],
        })
        flow.write_json(self.root / "build/build-manifest.json", {"source_sha256": stamp, "pdf_sha256": "fixture"})
        with patch.object(flow, "build"):
            flow.finish()
        self.assertEqual(flow.config()["phase"], "revision")
        self.assertEqual(flow.catalogue()[0]["status"], "resolved")
        queue = flow.read_json(self.root / "research/editorial/revision-queue.json")
        self.assertEqual(len(queue["units"]), len(flow.sources()))

    def test_revision_guard_blocks_source_on_main(self):
        cfg = flow.config(); cfg["phase"] = "revision"
        flow.write_json(self.root / "bookflow.json", cfg)
        with patch.object(flow, "run") as runner:
            runner.return_value.stdout = "book/chapters/01-foundations.tex\n"
            with self.assertRaisesRegex(ValueError, "revision"):
                flow.guard()
        self.branch_mock.return_value = "revision/fix-estimate"
        flow.guard()


if __name__ == "__main__":
    unittest.main()
