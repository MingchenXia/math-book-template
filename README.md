# Math book template

A reusable repository for writing mathematical books: chapter-based LaTeX, an automatic open-problem catalogue, separate solution folders, proof review, integration of approved solutions, and author-reviewed revisions after completion. All repository content is written in English.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/MingchenXia/math-book-template)

| Problems and solutions | Action |
| --- | --- |
| [View the Open Problem List](research/open-problems.md) | Find stable IDs, current status, manuscript locations and solution submission links |
| [Add an open problem](docs/manual-entry.md#add-an-open-problem) | Edit a chapter manually or use `problem-add` to insert it and synchronize the catalogue |
| [Submit an existing solution manually](docs/manual-entry.md#submit-an-existing-solution) | Upload a result and proof or use `solution-import` to create a candidate |
| [Solution folders](research/solutions/) | Store full or partial proofs and metadata by ID; independent review controls integration |

## Getting started

**Codex Cloud:** use the current **Work in → Cloud** environment flow. Select your repository and send the [cloud setup prompt](docs/codex-cloud.md) to the setup agent. It runs `bash scripts/setup-codex-cloud.sh` to install and verify the environment. Review the report and select Publish; new tasks can then select that environment. Hosted agents do not need an additional CLI/API login. Use `review-prepare` and `review-record` for independent review. Initial account connection and environment publication take place in the Codex interface.

**GitHub Codespaces:** select **Use this template → Create a new repository** for your book, then **Code → Codespaces → Create codespace**. The environment installs TeX, Biber, Python, PDF tools and a pinned Codex CLI, then compiles the demonstration book. The button above opens the template directly for a trial. The first container build downloads TeX; its duration depends on your connection.

With local TeX/Codex or Docker, one command prepares the environment and builds the PDF:

```sh
bash start.sh
```

Set the title and author in `bookflow.json`, define the readers and scope in `PLAN.md`, and replace the examples in `book/chapters/`. The PDF is `build/pdf/main.pdf`. The two demonstration questions are elementary exercises, not claims of open problems in the literature.

For dedicated CLI agents locally or in Codespaces, sign in to your own Codex account. The hosted workflow is described in the [cloud guide](docs/codex-cloud.md).

```sh
codex login
make edit       # Write/edit the current chapter and address review findings
make review     # Independent read-only review: mathematics, prose, sources, layout and a second pass
```

For a long book, review individual units with `python3 scripts/bookflow.py agent review --unit book/chapters/01-foundations.tex --pages 4`. Pages are physical PDF page numbers and must cover the assigned unit. Review the root document and preamble for global structure, bibliography and index settings as well. Before completion, every active input must have a current approved report for the same book fingerprint. Sampling does not replace a final review.

See [environment details](docs/environment.md) for tools and authentication. This template does not require private skills, reference libraries or validators from the author's computer.

## Writing the book

```text
book/chapters/             Chapters and preface
research/open-problems.*    Automatically generated problem catalogue
research/solutions/        Full or partial answers, one folder per problem
research/reviews/          Independent review reports and input fingerprints
research/editorial/        Book revision queue, baseline and proposals
references/papers/         Reference full texts, not committed publicly by default
references/notes/          Reading notes, exact versions and theorem locators
references/references.bib  The book's single bibliography
agents/                   Writing, editing, book review and solution review roles
```

Write a question in its chapter:

```tex
\BookProblem{OP-003}{Catalogue title}{State the precise question, with hypotheses and scope.}
```

`make sync` generates the [Open Problem List](research/open-problems.md). The catalogue records this book's proof obligations; a claim that a problem remains open in the literature requires separate verification. Builds, commit hooks and GitHub maintenance synchronize it. Run `make watch` explicitly if you want local updates while editing.

Store an answer in `research/solutions/OP-003/`, following the [solution guide](research/solutions/README.md), then run:

```sh
python3 scripts/bookflow.py agent solution-review --problem OP-003
make build
make review
```

A complete solution approved by independent review replaces the original question and preserves its reference label. Partial answers leave the full question unresolved. Changes to a proof or related input invalidate earlier approvals. Generated TeX is not committed; every machine rebuilds it from the same sources. The editor must check outdated statements, consequences and dependencies elsewhere in the book.

## Automatic checks and review

Every push/PR runs workflow tests, builds the same container environment and compiles the PDF. Actions preserves the PDF, source fingerprint and catalogue in a `book-<commit>` artifact.

`Book maintenance` updates the catalogue after manuscript/solution changes on the default branch and saves results as an Actions artifact. With an Actions secret named **OPENAI_API_KEY**, it also reviews new solutions and short books independently. Without that secret, it explicitly skips AI review and still synchronizes the catalogue. API use requires your own available account.

To opt into maintenance proposal PRs, set repository variable **ENABLE_MAINTENANCE_PRS=true** and enable the repository permission allowing GitHub Actions to create PRs. This option is off by default; the template does not approve or automatically merge PRs.

PRs created with the default `GITHUB_TOKEN` usually do not trigger another workflow automatically. Before merging a maintenance PR, run `Book checks` manually on `automation/book-maintenance` and inspect the matching PDF. No PR is created when nothing changed. No cron schedule or personal website publication is configured.

## Revising a completed book

The procedure follows [SGPT's revision workflow](https://github.com/MingchenXia/SGPT/blob/main/AGENTS.md): separate branches, actual change records, proof and dependency checks, PDF excerpts, proposal PRs, and explicit author approval of the current version before merge or publication.

Once the complete current manuscript passes review:

```sh
make finish
git add bookflow.json research CHANGELOG.md
git commit -m "Record the completed-book baseline"
python3 scripts/bookflow.py revision-start fix-estimate
# Edit revision/fix-estimate, update CHANGELOG.md and process the revision queue
make review
python3 scripts/bookflow.py revision-prepare --base main --pages 5-8 --summary "Correct the estimate's hypotheses and check affected consequences"
```

`--pages` uses physical PDF page numbers and must include every modified passage with sufficient context. The command prepares the full PDF, an excerpt, a diff and PR text. The author reviews the current PDF before merge; agent review does not substitute for author approval. See the [complete revision procedure](docs/revision.md) for PRs, renewed approval, publication and branch cleanup. Choose a publication destination when adapting the template.

## Validation and design sources

```sh
make test
make sync
make check
make build
```

The Python workflow uses only the standard library. Tests cover unreviewed, approved and partial solutions, stale reviews, paths and input graphs, and proposal branches after completion. TeX/Biber compilation is checked separately. These checks validate the workflow and build; mathematical reviewers must record only the scope actually read and reconstructed.

Drafting draws on the manuscript, blueprint, problem catalogue and audit roles in [non-kahler-pluripotential-theory](https://github.com/MingchenXia/non-kahler-pluripotential-theory); revisions draw on [SGPT](https://github.com/MingchenXia/SGPT). The code and examples were written independently. No private manuscript, paper or research archive was copied from those repositories. See [workflow details](docs/workflow.md) and the [validation record](docs/validation.md).
