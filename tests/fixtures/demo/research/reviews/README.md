# Review records

Independent reviewers use read-only tools and return JSON following `agents/review.schema.json`; the host saves the report. Each report binds the input SHA-256 and records only checks actually completed. Approval requires statement, proof, dependencies, sources and second_pass coverage, with no blocking or major findings.

`source_sha256` covers the relevant manuscript, single bibliography, original problem and candidate proof. Book reports also cover the solutions actually integrated. Relevant changes invalidate earlier conclusions. Manually filling in approved is a declaration, not evidence of independent review or formal verification. A writing agent must not create its own approval report.

The current problem report is `solution-<ID>.json`; the whole-book report is `book.json`. Git preserves history. Do not alter the scope claimed by an earlier review.
