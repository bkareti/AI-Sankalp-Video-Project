"""Static diagram primitives for section visuals: flow, steps, compare, table.

Each builder takes a normalized spec (see `specs.py`) and returns a VGroup
that fits inside `width` x `height`. All text comes from the spec.
"""
from __future__ import annotations

from typing import Any, Callable, Dict

from manim import DOWN, LEFT, RIGHT, UP, Arrow, Circle, Line, RoundedRectangle, VGroup

from .. import brand
from ..brand import BrandFonts
from .layout import fit, text, wrap_text


def flow_diagram(spec: Dict[str, Any], fonts: BrandFonts, width: float, height: float) -> VGroup:
    items = spec["items"]
    gap = 0.42
    node_height = min(0.92, (height - gap * (len(items) - 1)) / len(items))
    nodes = VGroup()
    for index, item in enumerate(items):
        color = brand.ACCENT_CYCLE[index % len(brand.ACCENT_CYCLE)]
        box = RoundedRectangle(
            width=width * 0.82, height=node_height, corner_radius=0.13,
            stroke_color=color, stroke_width=2, fill_color=brand.PANEL_2, fill_opacity=1,
        )
        label = fit(text(wrap_text(item, 34), fonts, 20, bold=True), box.width - 0.3, node_height - 0.14)
        nodes.add(VGroup(box, label.move_to(box)))
    nodes.arrange(DOWN, buff=gap)
    arrows = VGroup(*[
        Arrow(
            nodes[index].get_bottom(), nodes[index + 1].get_top(), buff=0.05,
            color=brand.ACCENT, stroke_width=2.5, max_tip_length_to_length_ratio=0.3,
        )
        for index in range(len(nodes) - 1)
    ])
    return fit(VGroup(nodes, arrows), width, height)


def steps_list(spec: Dict[str, Any], fonts: BrandFonts, width: float, height: float) -> VGroup:
    rows = VGroup()
    for index, item in enumerate(spec["items"]):
        color = brand.ACCENT_CYCLE[index % len(brand.ACCENT_CYCLE)]
        badge = Circle(radius=0.24, color=color, stroke_width=2.5, fill_color=brand.PANEL_2, fill_opacity=1)
        number = text(str(index + 1), fonts, 20, color=color, bold=True).move_to(badge)
        label = fit(text(wrap_text(item, 30), fonts, 21, line_spacing=0.85), width - 0.9)
        rows.add(VGroup(VGroup(badge, number), label).arrange(RIGHT, buff=0.25))
    rows.arrange(DOWN, buff=0.34, aligned_edge=LEFT)
    return fit(rows, width, height)


def compare_columns(spec: Dict[str, Any], fonts: BrandFonts, width: float, height: float) -> VGroup:
    column_width = (width - 0.3) / 2
    item_texts = {
        side: [text(wrap_text(item, 20), fonts, 19, line_spacing=0.85) for item in spec[side]["items"]]
        for side in ("left", "right")
    }
    # One shared scale so every item in both columns has the same type size.
    scale = min([1.0] + [(column_width - 0.3) / item.width for items in item_texts.values() for item in items])
    columns = VGroup()
    for side, color in (("left", brand.CORAL), ("right", brand.MINT)):
        data = spec[side]
        heading = fit(text(data["title"], fonts, 22, color=color, bold=True), column_width - 0.3)
        items = VGroup(*[item.scale(scale) for item in item_texts[side]]).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        body = VGroup(heading, items).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        box = RoundedRectangle(
            width=column_width, height=min(height, body.height + 0.6), corner_radius=0.14,
            stroke_color=color, stroke_width=2, fill_color=brand.PANEL_2, fill_opacity=1,
        )
        fit(body, column_width - 0.3, box.height - 0.3)
        body.move_to(box)
        columns.add(VGroup(box, body))
    columns.arrange(RIGHT, buff=0.3, aligned_edge=UP)
    return fit(columns, width, height)


def data_table(spec: Dict[str, Any], fonts: BrandFonts, width: float, height: float) -> VGroup:
    columns, rows = spec["columns"], spec["rows"]
    cell_width = width / len(columns)
    cell_height = min(0.62, height / (len(rows) + 1))
    labels = [
        [
            text(value, fonts, 20, color=brand.CYAN if row_index == 0 else brand.SOFT_WHITE,
                 bold=row_index == 0, mono=row_index != 0)
            for value in row
        ]
        for row_index, row in enumerate([columns] + rows)
    ]
    # One shared scale keeps every cell the same type size.
    scale = min([1.0] + [
        min((cell_width - 0.28) / label.width, (cell_height - 0.2) / label.height)
        for row in labels for label in row
    ])
    grid = VGroup()
    for row_index, row in enumerate(labels):
        is_header = row_index == 0
        cells = VGroup()
        for label in row:
            box = RoundedRectangle(
                width=cell_width - 0.08, height=cell_height - 0.08, corner_radius=0.06,
                stroke_color=brand.CYAN if is_header else brand.ACCENT, stroke_width=1.4,
                stroke_opacity=0.9 if is_header else 0.45,
                fill_color=brand.PANEL_2 if is_header else brand.PANEL, fill_opacity=1,
            )
            label.scale(scale)
            cells.add(VGroup(box, label.move_to(box)))
        cells.arrange(RIGHT, buff=0.08)
        grid.add(cells)
    grid.arrange(DOWN, buff=0.08)
    rule = Line(grid[0].get_corner(DOWN + LEFT), grid[0].get_corner(DOWN + RIGHT), color=brand.CYAN, stroke_width=2)
    return fit(VGroup(grid, rule), width, height)


SECTION_BUILDERS: Dict[str, Callable[[Dict[str, Any], BrandFonts, float, float], VGroup]] = {
    "flow": flow_diagram,
    "steps": steps_list,
    "compare": compare_columns,
    "table": data_table,
}


def build_section_visual(spec: Dict[str, Any], fonts: BrandFonts, width: float, height: float) -> VGroup:
    return SECTION_BUILDERS[spec["type"]](spec, fonts, width, height)
