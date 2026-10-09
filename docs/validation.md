# Template validation record

Initial template validation on 2026-10-07:

- All 22 standard-library tests passed, covering integration before/after approval, partial answers, stale input, binary figures, unit review composition, completion baselines and branch limits, input cycles, stable IDs, path boundaries and reference errors.
- Local `bash start.sh`, `make sync`, `make check` and pdfLaTeX/BibTeX/MakeIndex builds passed. The example PDF had six physical pages. Final logs contained no unresolved references or duplicate labels. Empty-bibliography and BibLaTeX BibTeX-fallback notices were retained.
- A real independent read-only Codex solution review ran in a temporary copy. Its complete report bound the current input, and the demonstration proof was incorporated. The public template retained its unreviewed candidate for practice.
- In the same temporary copy, the whole-book reviewer read twice and inspected all six PDF page images. It returned approved with three concrete editorial suggestions. The template clarified the ambient topology and made the chapter opening valid before and after integration. Temporary review records do not stand in for a new user's verification history.
- Both GitHub workflows passed YAML parsing. Python files passed syntax compilation and shell entry points passed syntax checks.

Refer to the repository's Book checks runs for actual container build results. Review records cover only what was read and reconstructed. Tests and PDF compilation do not certify a research book's mathematical correctness.

Codex Cloud integration validation on 2026-10-07:

- Ten assignment export/registration tests brought the total to 32 passing tests. They cover complete and partial solutions, needs_work, stale input, wrong assignments, incomplete approval, invalid formats, unit scope and path boundaries.
- `setup-codex-cloud.sh --verify-only` passed on the prepared local toolchain. A chapter assignment generated its exact input fingerprint and PDF page images.
- Both jobs in [Book checks / 5428d8c](https://github.com/MingchenXia/math-book-template/actions/runs/37601915607) succeeded. The Dev Container rebuilt and compiled. A fresh Ubuntu runner executed the native installation script, installed dependencies, ran tests and compiled the six-page book. Repeating setup also succeeded, without nested Codex CLI login or an API key.
- Real independent CLI proof review in a temporary Git copy passed the shared registration validation and integrated the demonstration answer. The public template retained the candidate and did not include temporary review history.
- Linux validation establishes script/build behavior, not creation or publication of an environment in a ChatGPT account. Actual cloud setup must run under the selected network policy, be reviewed and be published.

Manual problem/solution entry validation on 2026-10-07:

- Thirteen submission tests brought the total to 45 local passing tests. They cover catalogue synchronization, preserving chapters, duplicate IDs, unbalanced statements, reference-failure rollback, inactive inputs, unreviewed imports, partial scope, refusal of implicit overwrite, stale reviews after replacement, unknown problems, path boundaries and revision proposal branches.
- Actual `problem-add` and `solution-import` commands ran in a temporary copy. The original question remained, the imported answer stayed candidate, no review approval was created, and the six-page PDF compiled. That temporary problem and answer were not added to the public example.
- Manual entry links in the homepage, catalogue and solution README resolved, command help was available, and local `make check` and PDF builds passed. Refer to the corresponding Book checks run for Linux results.

English-language update validation on 2026-10-09:

- Translated all remaining Chinese repository prose, including test-fixture documentation and the catalogue generator. Scanning all 73 tracked files found no remaining Chinese text. The regenerated catalogue and its submission links are in English.
- All local Markdown file links and heading anchors resolved after translation.
- All 45 existing workflow tests, `make sync`, `make check` and the local PDF build passed. The mathematical manuscript was not changed, and no new mathematical approval was claimed.
