"""OpenAPI drift detection (Part 37 §X.3, §Z.2).

Verifies operation-level parity between the FastAPI-generated schema and the
committed `api/openapi.yaml`: no undocumented endpoint, no stale endpoint.
Additionally validates the committed contract is structurally sound — every
operation declares responses and every `$ref` resolves.
"""
from __future__ import annotations

import yaml

from .common import Check, OPENAPI_PATH, operation_set, HTTP_METHODS


def _generated_paths() -> dict:
    from app.main import app

    return app.openapi().get("paths", {})


def diff_operations(generated: set, committed: set) -> tuple[set, set]:
    """Pure diff: (undocumented = in code not in contract, stale = in contract not in code)."""
    return generated - committed, committed - generated


def _iter_refs(node):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "$ref" and isinstance(v, str):
                yield v
            else:
                yield from _iter_refs(v)
    elif isinstance(node, list):
        for item in node:
            yield from _iter_refs(item)


def check_openapi() -> Check:
    chk = Check("openapi")
    if not OPENAPI_PATH.exists():
        chk.fail(f"committed contract missing: {OPENAPI_PATH}")
        return chk

    spec = yaml.safe_load(OPENAPI_PATH.read_text(encoding="utf-8"))
    committed = spec.get("paths", {})
    generated = _generated_paths()

    gen_ops = operation_set(generated)
    com_ops = operation_set(committed)

    undocumented, stale = diff_operations(gen_ops, com_ops)
    for method, path in sorted(undocumented):
        chk.fail(f"undocumented endpoint (in code, not in openapi.yaml): {method} {path}")
    for method, path in sorted(stale):
        chk.fail(f"stale endpoint (in openapi.yaml, not in code): {method} {path}")

    # Structural soundness of the committed contract.
    for raw_path, item in committed.items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() in HTTP_METHODS and "responses" not in op:
                chk.fail(f"operation {method.upper()} {raw_path} declares no responses")

    schema_names = set((spec.get("components", {}).get("schemas", {})).keys())
    for ref in _iter_refs(spec):
        if ref.startswith("#/components/schemas/"):
            name = ref.rsplit("/", 1)[-1]
            if name not in schema_names:
                chk.fail(f"dangling $ref: {ref}")

    chk.info["generated_ops"] = len(gen_ops)
    chk.info["committed_ops"] = len(com_ops)
    return chk
