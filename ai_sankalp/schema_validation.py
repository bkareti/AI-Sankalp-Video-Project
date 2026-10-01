"""A small, dependency-free JSON Schema validator for the project's own schemas.

Only the keyword subset used by ``templates/*.schema.json`` is supported, so
unit tests and the CLI can validate lessons offline without ``jsonschema``.
Unsupported keywords raise :class:`SchemaError` instead of being ignored.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates"

ANNOTATIONS = {
    "$schema", "$id", "title", "description", "default", "examples",
    "$comment", "$defs", "deprecated",
}
SUPPORTED = {
    "type", "required", "properties", "additionalProperties", "items",
    "minItems", "maxItems", "minLength", "maxLength", "pattern", "enum",
    "const", "minimum", "maximum", "oneOf", "anyOf", "allOf", "$ref",
}


class SchemaError(ValueError):
    """Raised when a schema uses a keyword this validator does not implement."""


@dataclass(frozen=True)
class SchemaIssue:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path or '(root)'}: {self.message}"


def load_schema(name: str) -> Dict[str, Any]:
    return json.loads((TEMPLATES_DIR / name).read_text(encoding="utf-8"))


def _child(path: str, key: Any) -> str:
    if isinstance(key, int):
        return f"{path}[{key}]"
    return f"{path}.{key}" if path else str(key)


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "string":
        return isinstance(value, str)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "null":
        return value is None
    raise SchemaError(f"unsupported type name: {expected}")


def _resolve_ref(ref: str, root: Dict[str, Any]) -> Dict[str, Any]:
    if not ref.startswith("#/"):
        raise SchemaError(f"only local $ref values are supported: {ref}")
    node: Any = root
    for part in ref[2:].split("/"):
        if not isinstance(node, dict) or part not in node:
            raise SchemaError(f"unresolvable $ref: {ref}")
        node = node[part]
    return node


def _describe(value: Any) -> str:
    text = json.dumps(value, ensure_ascii=False)
    return text if len(text) <= 40 else text[:37] + "..."


def _validate(instance: Any, schema: Any, root: Dict[str, Any], path: str) -> List[SchemaIssue]:
    if schema is True or schema == {}:
        return []
    if schema is False:
        return [SchemaIssue(path, "is not allowed")]
    if not isinstance(schema, dict):
        raise SchemaError(f"schema at {path or '(root)'} must be an object or boolean")
    unknown = set(schema) - SUPPORTED - ANNOTATIONS
    if unknown:
        raise SchemaError(f"unsupported schema keyword(s): {', '.join(sorted(unknown))}")

    if "$ref" in schema:
        issues = _validate(instance, _resolve_ref(schema["$ref"], root), root, path)
        rest = {key: value for key, value in schema.items() if key != "$ref"}
        return issues + _validate(instance, rest, root, path) if set(rest) - ANNOTATIONS else issues

    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_type_ok(instance, name) for name in types):
            return [SchemaIssue(path, f"must be of type {' or '.join(types)}")]

    issues: List[SchemaIssue] = []
    if "const" in schema and instance != schema["const"]:
        issues.append(SchemaIssue(path, f"must equal {_describe(schema['const'])}"))
    if "enum" in schema and instance not in schema["enum"]:
        allowed = ", ".join(_describe(item) for item in schema["enum"])
        issues.append(SchemaIssue(path, f"must be one of: {allowed}"))

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            issues.append(SchemaIssue(path, f"must have at least {schema['minLength']} character(s)"))
        if "maxLength" in schema and len(instance) > schema["maxLength"]:
            issues.append(SchemaIssue(path, f"must have at most {schema['maxLength']} character(s)"))
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            issues.append(SchemaIssue(path, f"{_describe(instance)} does not match {schema['pattern']}"))

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            issues.append(SchemaIssue(path, f"must be >= {schema['minimum']}"))
        if "maximum" in schema and instance > schema["maximum"]:
            issues.append(SchemaIssue(path, f"must be <= {schema['maximum']}"))

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            issues.append(SchemaIssue(path, f"must have at least {schema['minItems']} item(s)"))
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            issues.append(SchemaIssue(path, f"must have at most {schema['maxItems']} item(s)"))
        if "items" in schema:
            for index, item in enumerate(instance):
                issues.extend(_validate(item, schema["items"], root, _child(path, index)))

    if isinstance(instance, dict):
        for name in schema.get("required", []):
            if name not in instance:
                issues.append(SchemaIssue(_child(path, name), "is required"))
        properties = schema.get("properties", {})
        for name, value in instance.items():
            if name in properties:
                issues.extend(_validate(value, properties[name], root, _child(path, name)))
            elif "additionalProperties" in schema:
                issues.extend(_validate(value, schema["additionalProperties"], root, _child(path, name)))

    for sub in schema.get("allOf", []):
        issues.extend(_validate(instance, sub, root, path))
    if "anyOf" in schema:
        branches = [_validate(instance, sub, root, path) for sub in schema["anyOf"]]
        if all(branches):
            issues.extend(min(branches, key=len))
    if "oneOf" in schema:
        branches = [_validate(instance, sub, root, path) for sub in schema["oneOf"]]
        matches = sum(1 for branch in branches if not branch)
        if matches == 0:
            issues.extend(min(branches, key=len))
        elif matches > 1:
            issues.append(SchemaIssue(path, "matches more than one allowed form"))
    return issues


def validate(instance: Any, schema: Dict[str, Any]) -> List[SchemaIssue]:
    """Return every schema violation in ``instance`` (empty when valid)."""
    return _validate(instance, schema, schema, "")
