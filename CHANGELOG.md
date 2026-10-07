# Change log

Record substantive updates here with the author's date, actual changed passages, and checks actually performed. Preserve old entries. Do not describe reviewed-but-unchanged text as a correction.

## 2026-10-07 — Template baseline

Added a demonstration book, problem discovery, separate solution storage and review, automatic integration of current approved full solutions, a dedicated writing/review/editor workflow, and the completed-book proposal procedure. Local and CI validation are recorded in the template's release documentation.

The completed template supports current full-book or per-input reviews, PDF preview/excerpt generation and input fingerprints covering styles, figures and references. Twenty-two workflow tests and the native PDF build passed. Real CLI proof and whole-book review were exercised in isolated demonstration copies; the public baseline retains the original candidate state. Clarified the example's ambient topology and chapter transition following that review. Maintenance defaults to report artifacts; PR proposals require explicit opt-in, while PR approval permissions remain disabled.

The first Linux compile identified Debian's separate biblatex package; added `texlive-bibtex-extra` explicitly and package probes during image construction. Container command sequences stop on the first failed check. A fresh source clone rebuilt successfully on the native toolchain.
