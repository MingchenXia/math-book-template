# Codex Cloud book environment

This template can run in **Codex Cloud**. Initial setup requires selecting a GitHub repository, verifying installation and selecting Publish. Later, choose the published environment under **Work in → Cloud**. The account connection and publication steps take place in Codex; the Codespaces button opens a different environment. Follow the [official cloud environment guide](https://learn.chatgpt.com/docs/environments/cloud-environments).

## Initial setup

Use **Use this template** to create a repository for your own book. You can select `MingchenXia/math-book-template` for a trial, but save a new book in its own repository.

In a new desktop or web task, choose **Work in → Cloud → Select environment → Create environment**, or use **Settings → Codex Cloud → Environments**. Select the new GitHub repository. If GitHub is not connected, complete the connection and repository selection in the interface.

After selecting **Get started**, send this prompt to the environment setup agent:

```text
Configure a mathematical book environment for the selected repository derived from math-book-template.
From that repository's checkout root, run bash scripts/setup-codex-cloud.sh.
Record the tested command as the Install script; with multiple repositories, first cd to this repository.
Use the Debian/Ubuntu packages in .devcontainer/tex-packages.txt.
Package managers network access is needed to download official system packages.
Use the hosted Codex agent; do not require nested CLI login or OPENAI_API_KEY.
Set the Start skill according to docs/codex-cloud-start.md, checking and building from this task's repository root.
Verify make doctor, make test, make sync, make check and make build.
Confirm build/pdf/main.pdf exists and report its physical page count.
Only prepare the environment. Leave demonstration candidates unapproved and do not fabricate review reports.
Show installation, test and build results, and the configuration to save, for my review and publication.
```

**Allow Codex to access internet → Package managers** covers the Debian/Ubuntu repositories used here. Add other required sites when checking papers; access to a site does not establish access to its full text. Review the setup report, save the configuration and select **Publish**. Start a book task after **Environment published** appears. See the [official setup, network and publication procedure](https://learn.chatgpt.com/docs/environments/cloud-environments#create-and-publish-an-environment).

The installation script is repeatable and skips downloads for packages already installed. It directly installs TeX, BibTeX/Biber, CJK fonts, Python and Poppler, configures hooks, synchronizes the catalogue, runs tests and compiles the book. No Docker is needed; Codespaces uses the same system package manifest. `--verify-only` checks a prepared machine without installing software. Resolve installation failures in the setup conversation and retry. Installation does not provide mathematical review.

## Hosted writing and independent review

Ask the hosted agent to work on a specified chapter under `AGENTS.md` and `agents/edit.md`, then run `make sync && make check && make build`. Its account does not automatically authenticate a nested `codex exec` process. `make edit` and `make review` remain CLI entry points requiring separate login. The assignment export and registration commands below allow independent review using hosted agents without that extra CLI/API configuration.

Prepare an assignment for a candidate answer:

```sh
python3 scripts/bookflow.py review-prepare solution-review --problem OP-001
```

For the book or a bounded chapter:

```sh
python3 scripts/bookflow.py review-prepare review
python3 scripts/bookflow.py review-prepare review --unit book/chapters/01-foundations.tex --pages 4
```

The command prints paths to `build/review-packets/<fingerprint>/assignment.json` and `prompt.md`. Book review first compiles and renders PDF pages. Give the prompt to an **independent, read-only reviewer**. If the cloud task supports subagents, delegate to a fresh read-only reviewer. Otherwise use a separate review task on the same branch and version, regenerating its assignment. The writer cannot fill in its own approved report. Reference full texts needed for review must also be available in the review environment.

The independent reviewer returns JSON matching `agents/review.schema.json`. The host preserves the actual response in a repository-local file such as `build/cloud-review.json`. Register it using the assignment path printed by the preparation command:

```sh
python3 scripts/bookflow.py review-record \
  --assignment build/review-packets/<fingerprint>/assignment.json \
  --report build/cloud-review.json
make build
```

Registration checks report format, scope, the current input fingerprint and coverage including a second reading. Stale or incomplete approvals are rejected. needs_work/rejected leave the question unresolved; only complete, currently approved answers enter the manuscript. JSON and fingerprints record scope and consistency, not reviewer identity or mathematical correctness. A reviewer unable to inspect the PDF must report the missing layout check and cannot claim that final review is complete.

The problem catalogue, solution folders, references and `revision/*` proposal procedure are the same in cloud tasks. GitHub Actions AI review is a separate execution path; selecting Codex Cloud does not supply an Actions API key.

## Saving and updating

Commit important sources and create PRs; environment snapshots do not replace Git. New tasks use the published prepared state. Existing tasks retain their own files and tools, and repository refresh does not rerun installation automatically. When dependencies change, open **Settings → Codex Cloud → Environments → Edit**, request installation and tests, save and **Republish**, then verify in a new task. See the [official saved-state guide](https://learn.chatgpt.com/docs/environments/cloud-environments#reuse-and-update-saved-state).

Personal local skills do not automatically synchronize to the cloud. The template keeps `AGENTS.md`, `agents/` and scripts in the repository and does not require private skills. Keep personal login files, API keys and reference full texts without redistribution permission out of the public repository.

If your account only provides **Codex Cloud (Legacy)** Setup script configuration, use the same installation command with the [legacy environment guide](https://learn.chatgpt.com/docs/environments/cloud-environment). That experience primarily retains Code Review and GitHub/Linear integrations; its settings differ from the current Install script and Start skill flow.
