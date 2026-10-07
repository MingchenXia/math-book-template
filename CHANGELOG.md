# Change log

Record substantive updates here with the author's date, actual changed passages, and checks actually performed. Preserve old entries. Do not describe reviewed-but-unchanged text as a correction.

## 2026-10-07 — Codex Cloud setup

Added a repeatable native Debian/Ubuntu install-and-verify command for current Codex Cloud, using the same TeX package manifest as the Dev Container. Added current environment creation, Install script, Start skill and publish instructions, with explicit first-time account setup. Hosted cloud reviewers can export source-bound assignments and register independently produced structured reports without a nested CLI login; existing CLI review uses the same validation. The writer still cannot approve its own candidate, and stale or incomplete approvals remain rejected. Cloud deployment itself must be validated in the user's selected cloud environment before publishing it.

All 32 tests, native PDF compilation, real independent CLI review in a temporary copy, and fresh Ubuntu installation/repeated setup passed. The updated Dev Container also rebuilt and compiled successfully. The selected user's Codex Cloud environment has not been created or published by this repository update; validation links and scope are recorded in docs/validation.md.

## 2026-10-07 — Template baseline

Added a demonstration book, problem discovery, separate solution storage and review, automatic integration of current approved full solutions, a dedicated writing/review/editor workflow, and the completed-book proposal procedure. Local and CI validation are recorded in the template's release documentation.

The completed template supports current full-book or per-input reviews, PDF preview/excerpt generation and input fingerprints covering styles, figures and references. Twenty-two workflow tests and the native PDF build passed. Real CLI proof and whole-book review were exercised in isolated demonstration copies; the public baseline retains the original candidate state. Clarified the example's ambient topology and chapter transition following that review. Maintenance defaults to report artifacts; PR proposals require explicit opt-in, while PR approval permissions remain disabled.

The first Linux compile identified Debian's separate biblatex package; added `texlive-bibtex-extra` explicitly and package probes during image construction. Container command sequences stop on the first failed check. A fresh source clone rebuilt successfully on the native toolchain.
