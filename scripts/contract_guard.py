#!/usr/bin/env python3
"""Flag PRs that touch frozen contract paths without a tech.md version bump (tech.md, section 3).

Mode comes from the tech.md header at HEAD: "Каркас: не готов" warns, "Каркас: готов" fails.
The PR label "no-contract-change" bypasses the check for edits that keep the interface.
"""

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys

FROZEN = (
    "contracts/**",
    "backend/apps/*/migrations/**",
    "backend/apps/core/enums.py",
    "backend/apps/leads/sheets/row.py",
    "backend/apps/leads/messenger/text.py",
    "frontend/src/lib/types/**",
    "frontend/src/lib/server/api.ts",
    "frontend/src/lib/components/ui/**",
    ".env.example",
)
BYPASS_LABEL = "no-contract-change"
VERSION_RE = re.compile(r"^- Версия: (v\d+)\s*$", re.MULTILINE)
READY_RE = re.compile(r"^- Каркас: (готов|не готов)\s*$", re.MULTILINE)


def git(*args: str) -> str:
    result = subprocess.run(["git", *args], check=True, capture_output=True)
    return result.stdout.decode("utf-8")


def header(text: str) -> tuple[str, bool]:
    version, ready = VERSION_RE.search(text), READY_RE.search(text)
    if not version or not ready:
        raise SystemExit("contract-guard: tech.md header lacks 'Версия' or 'Каркас'")
    return version.group(1), ready.group(1) == "готов"


def pr_labels(cli_value: str | None) -> set[str]:
    if cli_value is not None:
        return {label.strip() for label in cli_value.split(",") if label.strip()}
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        return set()
    with open(event_path, encoding="utf-8") as event_file:
        event = json.load(event_file)
    return {label["name"] for label in event.get("pull_request", {}).get("labels", [])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    base_ref = os.environ.get("GITHUB_BASE_REF")
    parser.add_argument("--base", default=f"origin/{base_ref}" if base_ref else "origin/main")
    parser.add_argument("--labels", help="comma-separated PR labels; default: GitHub event")
    args = parser.parse_args(argv)

    merge_base = git("merge-base", args.base, "HEAD").strip()
    changed = git("diff", "--name-only", merge_base, "HEAD").split()
    touched = [path for path in changed if any(fnmatch.fnmatch(path, p) for p in FROZEN)]
    if not touched:
        print("contract-guard: no frozen paths touched")
        return 0

    print("contract-guard: frozen paths touched:")
    for path in touched:
        print(f"  {path}")

    base_version, _ = header(git("show", f"{merge_base}:tech.md"))
    head_version, ready = header(git("show", "HEAD:tech.md"))
    if head_version != base_version:
        print(f"contract-guard: tech.md bumped {base_version} -> {head_version}, ok")
        return 0
    if BYPASS_LABEL in pr_labels(args.labels):
        print(f"contract-guard: label '{BYPASS_LABEL}' set, ok")
        return 0
    message = f"frozen paths changed without a tech.md version bump (still {head_version})"
    if not ready:
        print(f"::warning::contract-guard: {message}; framework not ready, warning only")
        return 0
    print(f"::error::contract-guard: {message}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
