# i18n — machine-readable glossary

Source of truth: **`glossary.json`** (mirrors `MASTER_SPEC/28_ONTOLOGY_AND_GLOSSARY.md`).
Each term: `{ "id": canonical_id, "domain": ..., "en": ..., "ar": ... }`.

## Build locale maps
```bash
python i18n/build.py    # → en.json, ar.json  ({canonical_id: label})
```
`build.py` also fails if any `canonical_id` is duplicated.

## Usage
- **Code/data:** use the `canonical_id` everywhere (matches the enums in `schema/schema.sql` and `api/openapi.yaml`).
- **UI:** load `en.json` or `ar.json` and render by `canonical_id`. Arabic is **RTL**.
- **Governance:** add a new term to `glossary.json` first, then `build.py`, then use it.
