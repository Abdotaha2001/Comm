"""CLI entrypoint: run all Part 37 governance validators + emit the build manifest.

Usage:
    python -m tools.governance                 # validate + write build_manifest.json
    python -m tools.governance --no-manifest   # validate only
    python -m tools.governance --manifest PATH # custom manifest location

Exit code is non-zero if any governance check fails (CI gate, Part 37 §Z.9).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import run_all
from .common import BACKEND_ROOT
from .manifest import write_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Part 37 governance enforcement")
    parser.add_argument("--manifest", default=str(BACKEND_ROOT / "build_manifest.json"))
    parser.add_argument("--no-manifest", action="store_true")
    parser.add_argument("--json", action="store_true", help="emit machine-readable report")
    args = parser.parse_args(argv)

    ok, checks = run_all()

    if args.json:
        print(json.dumps({"ok": ok, "checks": [c.to_dict() for c in checks]}, indent=2))
    else:
        print("=" * 64)
        print("PART 37 — GOVERNANCE ENFORCEMENT REPORT")
        print("=" * 64)
        for c in checks:
            status = "PASS" if c.ok else "FAIL"
            print(f"[{status}] {c.name}")
            for e in c.errors:
                print(f"        - {e}")
        print("-" * 64)
        print("RESULT:", "ALL CHECKS PASSED" if ok else "GOVERNANCE FAILURES DETECTED")

    if not args.no_manifest:
        manifest = write_manifest(Path(args.manifest))
        if not args.json:
            print(f"\nbuild manifest -> {args.manifest}")
            print(f"  migration={manifest['migration_revision']} "
                  f"routes={manifest['route_checksum'][:18]}… "
                  f"state={manifest['repository_state']}")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
