# Cloud Start skill

Use these instructions in the cloud environment's Start skill field.

Locate the selected mathematical book repository and work from its checkout root.
Read AGENTS.md, bookflow.json, PLAN.md, BLUEPRINT.md, research/STATUS.md and any revision queue.
Run `make doctor`, `make sync`, `make check`, and `make build`. Confirm the PDF path
and its physical page count with pdfinfo. Stop and report a missing dependency or
build failure; do not silently skip it. The installation script is
`bash scripts/setup-codex-cloud.sh` and belongs to the environment setup flow.
Dependency changes require tested setup and republishing for future tasks.

Use the hosted Codex agent for the user's writing task and agents/edit.md for its
role. Do not assume an authenticated nested Codex CLI or OPENAI_API_KEY is present.
For independent review, use bookflow.py review-prepare and a fresh read-only
reviewer; record its actual structured response using review-record. Follow
docs/codex-cloud.md. The writer cannot approve its own proof. If no independent
reviewer is available, leave the candidate unapproved and describe the remaining
review step. In revision phase, mathematical changes require a proposal branch,
matching PDF excerpts and explicit author approval before merge or publication.

Do not start a watcher, scheduler, or web service as part of startup. Commit
important source changes or save needed outputs; prepared environment state is
not a replacement for source control.
