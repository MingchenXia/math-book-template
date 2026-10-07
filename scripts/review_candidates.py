#!/usr/bin/env python3
"""Review stale/unreviewed candidates, without rewriting accepted reports."""
import bookflow


if __name__ == "__main__":
    for record in bookflow.catalogue():
        if record["status"] in {"candidate", "review_stale"}:
            bookflow.agent("solution-review", record["id"])
