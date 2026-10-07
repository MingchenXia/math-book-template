#!/usr/bin/env python3
"""Optional local watcher. Started by the user; no background service is installed."""
import hashlib
from pathlib import Path
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]


def fingerprint():
    paths = [ROOT / "bookflow.json"]
    for folder, pattern in (("book", "*.tex"), ("research/solutions", "*"), ("research/reviews", "*.json"), ("references", "*.bib")):
        paths += [p for p in (ROOT / folder).rglob(pattern) if p.is_file() and "generated" not in p.parts]
    value = hashlib.sha256()
    for p in sorted(paths):
        value.update(str(p).encode()); value.update(p.read_bytes())
    return value.digest()


if __name__ == "__main__":
    previous = None
    print("Watching book, solutions, reviews and bibliography. Ctrl-C stops.", flush=True)
    try:
        while True:
            try:
                current = fingerprint()
                if current != previous:
                    time.sleep(0.5)
                    if fingerprint() == current:
                        subprocess.run(["python3", "scripts/bookflow.py", "sync"], cwd=ROOT, check=False)
                        previous = current
            except FileNotFoundError:
                pass  # Wait for an editor's atomic file replacement to finish.
            time.sleep(2)
    except KeyboardInterrupt:
        print("Watcher stopped.")
