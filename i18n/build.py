#!/usr/bin/env python3
"""Generate flat locale maps (en.json, ar.json) from glossary.json.

The glossary is the single source of truth (MASTER_SPEC Part 28). Run:
    python i18n/build.py
Produces i18n/en.json and i18n/ar.json as {canonical_id: label}.
Also validates that canonical_ids are unique.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).parent
SRC = HERE / "glossary.json"


def main() -> int:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    terms = data["terms"]

    ids = [t["id"] for t in terms]
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        print(f"ERROR: duplicate canonical_ids: {dupes}", file=sys.stderr)
        return 1

    for locale in ("en", "ar"):
        mapping = {t["id"]: t[locale] for t in terms}
        out = HERE / f"{locale}.json"
        out.write_text(
            json.dumps(mapping, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"wrote {out.name}: {len(mapping)} terms")

    print(f"OK · {len(terms)} terms · version {data.get('version')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
