# Manuscript, problem and solution workflow

The manuscript is the only source of problem statements. The three `BookProblem` arguments are a stable ID, catalogue title and original TeX statement. The parser follows static `\input{...}` and `\include{...}` commands from the root file, handling nested braces and comments. Input paths are relative to the root TeX directory. This lightweight parser does not support conditional alternative inputs, macro-computed paths, apparent inputs inside verbatim text or repeated inputs. Extend the parser and tests before using those forms; do not silently omit problems.

| Status | Meaning | Replaces the original question? |
| --- | --- | --- |
| open | No candidate answer | No |
| candidate | Answer saved without a valid current review | No |
| needs_work / rejected | Candidate has a gap or fails | No |
| review_stale | Relevant input changed after review | No |
| partial | A partial answer has been checked | No |
| resolved | Complete answer is current and eligible on this branch | Yes |
| verified_pending_revision | Verified after completion, awaiting a proposal branch | No |

Candidate metadata and complete proofs live in `research/solutions/ID/`; reports live in `research/reviews/`. The writer/editor uses workspace-write, and the reviewer runs a fresh read-only CLI session whose structured response is saved by the host. Writers must not approve their own results. Human review reports can be stored, but approved and SHA-256 are consistency records, not identity authentication or formal proof.

Hosted cloud agents or other independent reviewers can export an assignment with `review-prepare` and register the actual returned JSON with `review-record`. CLI review uses the same format, scope, current fingerprint and coverage checks. Independent read-only review remains required; importing a report does not authenticate its reviewer. See the [Codex Cloud guide](codex-cloud.md).

Approval requires statement, proof, dependencies, sources and a second complete reading. Book reports must also distinguish actual PDF layout inspection. A reviewer unable to read the entire book should return needs_work and identify the next bounded chapter, rather than approve from samples. For long books, use `research/editorial/revision-queue.json` to divide complete chapter reviews into finite units and record the actual scope in STATUS. Verify coverage of every input before final review.

For chapter review, run `python3 scripts/bookflow.py agent review --unit book/chapters/01-foundations.tex --pages 4-12`. The workflow compiles and renders the selected physical pages for the read-only reviewer. The root document, preamble and every active recursive input need current approved chapter reports for the same book fingerprint. Source changes invalidate those reports. Books over 60 pages require bounded unit reviews. If GitHub's short-book review step fails, completed solution reviews remain available. Selecting pages does not establish that every modified passage was included; report the actual scope inspected.

Changes to manuscript or bibliography fingerprints invalidate related solution approvals. Changes to the set of integrated solutions also invalidate whole-book approval. Preserve earlier reports in Git history; do not fabricate continuing approval. Each sync/build recreates generated files and removes obsolete generated proofs.

Fingerprints cover figures, styles, templates, build settings and locally available reference files/notes. Reference full texts are not publicly committed by default. A report made with those files becomes stale on a machine lacking the same references; a different reference version cannot stand in for the reviewed input.

A complete answer becomes a semantic proposition/theorem and proof at the original question's reading position, preserving the `prob:ID` alias. All proof dependencies must be available there. To place a result in another chapter, the editor must reorganize within authorization, preserve the ID, repair references and obtain another review. Macro replacement does not update statements elsewhere saying that the problem remains open; those checks belong to the editor.

`make sync`, builds, commit hooks and default-branch maintenance provide synchronization. Run `make watch` explicitly for local updates while editing. GitHub reviewers read sources without modifying them and upload report artifacts by default. Maintenance PRs require an explicit opt-in and repository permission. Automation does not merge mathematical revisions or publish a website. `make finish` records the baseline and changes phase to revision; newly verified solutions then require a proposal branch for integration.
