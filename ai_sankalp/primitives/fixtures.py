"""Primitive fixtures (examples/primitives/*.json) as one-scene packages."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "examples" / "primitives"


def fixture_paths(fixture_dir: Path = FIXTURE_DIR) -> List[Path]:
    return sorted(fixture_dir.glob("*.json"))


def smoke_class_name(kind: str) -> str:
    return "".join(part.capitalize() for part in kind.split("_")) + "Smoke"


def fixture_scene(fixture: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Return (scene, package) so a fixture plans and plays like a package scene."""
    examples = fixture.get("code_examples") or []
    scene = {
        "id": f"scene_{fixture['visual']['type']}",
        "type": "explanation",
        "title": fixture["visual"].get("title", ""),
        "voiceover": fixture["narration"],
        "visuals": [fixture["visual"]],
        "code_example_ids": [examples[0]["id"]] if examples else [],
    }
    package = {"language": fixture.get("language", ""), "code_examples": examples, "scenes": [scene]}
    return scene, package


def load_fixture(path: Path) -> Dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
