"""Smoke renders: one silent scene per primitive fixture in examples/primitives/.

Render one:  .venv/bin/python -m manim -ql scenes/primitive_smoke.py LoopTraceSmoke
List them:   .venv/bin/python scenes/primitive_smoke.py
"""
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from manim import Scene

from ai_sankalp.brand import brand_fonts
from ai_sankalp.primitives.base import PrimitiveContext
from ai_sankalp.primitives.fixtures import fixture_paths, fixture_scene, load_fixture, smoke_class_name
from ai_sankalp.primitives.frame import add_brand_frame
from ai_sankalp.primitives.planner import plan_lesson
from ai_sankalp.primitives.runner import play_scene


def make_smoke_scene(path: Path):
    fixture = load_fixture(path)

    class PrimitiveSmoke(Scene):
        def construct(self) -> None:
            fonts = brand_fonts()
            frame = add_brand_frame(self, fonts, style="grid")
            scene, package = fixture_scene(fixture)
            ctx = PrimitiveContext(
                fonts=fonts, package=package, scene_data=scene,
                project_root=PROJECT_ROOT, language=fixture.get("language", ""),
            )
            play_scene(self, plan_lesson(package)[0], ctx, voiceover=False, ambient=frame.ambient)
            self.wait(0.5)

    PrimitiveSmoke.__name__ = PrimitiveSmoke.__qualname__ = smoke_class_name(path.stem)
    return PrimitiveSmoke


for _path in fixture_paths():
    _scene_class = make_smoke_scene(_path)
    globals()[_scene_class.__name__] = _scene_class

if __name__ == "__main__":
    for _path in fixture_paths():
        print(smoke_class_name(_path.stem))
