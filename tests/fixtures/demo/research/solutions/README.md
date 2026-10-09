# Solutions to open problems

Use one folder per stable ID, such as `OP-001/`, containing `solution.json` and the complete `solution.tex`. The proof file uses the book's `proposition/theorem/lemma/corollary` and `proof` environments. Only self-contained TeX is supported; add new problems to a chapter.

Set metadata `scope` to `full` or `partial`, list manuscript labels in `dependencies`, and list keys from the single bibliography in `references`. After saving the answer, run:

```sh
python3 scripts/bookflow.py agent solution-review --problem OP-001
make build
make review
```

When a complete solution passes independent review and its fingerprint matches the current input, `make sync` incorporates the proof at the original problem location and preserves the `prob:OP-001` reference alias. A partial solution leaves the original question in place. Within the author's authorization, the editor should organize proved special cases and state the remaining question precisely, then request another review. Do not edit `book/generated/`.

Rejecting a candidate does not resolve the problem by counterexample. A genuine counterexample solution must also be fully stated, proved and reviewed, with `full` scope. Never reuse a problem ID.
