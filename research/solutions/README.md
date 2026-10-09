# Solutions to open problems

[Submit a full or partial solution manually](../../docs/manual-entry.md#submit-an-existing-solution) · [Open Problem List](../open-problems.md) · [Metadata template](../../docs/templates/solution.json) · [Result and proof template](../../docs/templates/solution.tex)

To import an answer written elsewhere, run `python3 scripts/bookflow.py solution-import --problem OP-002 --file work/answer.tex --scope full` from the repository root. You can also create the two files for the problem ID directly in GitHub's web interface. Import does not create review approval. See the manual entry guide above for submission, updates, PRs and proposal branches after completion.

Use one folder per stable ID, such as `OP-001/`, containing `solution.json` and the complete `solution.tex`. The proof file uses the book's `proposition/theorem/lemma/corollary` and `proof` environments. Only self-contained TeX is supported; add new problems to a chapter.

Set metadata `scope` to `full` or `partial`, list manuscript labels in `dependencies`, and list keys from the single bibliography in `references`. After saving the answer, run:

```sh
python3 scripts/bookflow.py agent solution-review --problem OP-001
make build
make review
```

When a complete solution passes independent review and its fingerprint matches the current input, `make sync` incorporates the proof at the original problem location and preserves the `prob:OP-001` reference alias. A partial solution leaves the original question in place. Within the author's authorization, the editor should organize proved special cases and state the remaining question precisely, then request another review. Do not edit `book/generated/`.

Rejecting a candidate does not resolve the problem by counterexample. A genuine counterexample solution must also be fully stated, proved and reviewed, with `full` scope. Never reuse a problem ID.
