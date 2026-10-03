"""Burn captions into a copy of the video (Pillow cue images + ffmpeg overlay).

The local ffmpeg build may lack libass (`subtitles`) and freetype
(`drawtext`), so each cue is drawn once as a transparent full-frame PNG in
the brand caption band and composited with ffmpeg's `overlay` filter.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

from . import brand
from .captions import Cue

VIDEO_SIZES = {
    "low": (854, 480),
    "medium": (1280, 720),
    "high": (1920, 1080),
    "production": (2560, 1440),
    "4k": (3840, 2160),
}
BOX_OPACITY = 0.8
MAX_TEXT_WIDTH = 0.86


class CaptionBurnError(RuntimeError):
    pass


def _hex_rgb(value: str) -> Tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[index:index + 2], 16) for index in (0, 2, 4))


def _load_font(font_file: Optional[Path], size: int):
    from PIL import ImageFont

    if font_file is not None:
        try:
            return ImageFont.truetype(str(font_file), size=size)
        except OSError:
            pass
    return ImageFont.load_default(size=size)


def render_cue_image(cue: Cue, size: Tuple[int, int], path: Path, font_file: Optional[Path] = None) -> Path:
    """Draw one cue as a transparent PNG whose pixels stay inside the caption band."""
    from PIL import Image, ImageDraw

    width, height = size
    band_top, band_bottom = brand.caption_band_pixels(height)
    band_height = band_bottom - band_top
    lines = cue.text.split("\n")[:2]
    font_size = max(10, int(band_height * 0.34))
    while True:
        font = _load_font(font_file, font_size)
        draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        boxes = [draw.textbbox((0, 0), line, font=font) for line in lines]
        line_height = max(box[3] - box[1] for box in boxes) if boxes else font_size
        text_width = max((box[2] - box[0] for box in boxes), default=0)
        pad_x, pad_y, spacing = int(font_size * 0.6), int(font_size * 0.25), int(font_size * 0.2)
        box_height = len(lines) * line_height + (len(lines) - 1) * spacing + 2 * pad_y
        fits = text_width + 2 * pad_x <= width * MAX_TEXT_WIDTH and box_height <= band_height
        if fits or font_size <= 10:
            break
        font_size -= 1

    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    box_width = text_width + 2 * pad_x
    left = (width - box_width) // 2
    top = band_top + max(0, (band_height - box_height) // 2)
    draw.rounded_rectangle(
        [left, top, left + box_width, top + box_height], radius=int(font_size * 0.35),
        fill=_hex_rgb(brand.BG) + (int(255 * BOX_OPACITY),),
    )
    y = top + pad_y
    for line, box in zip(lines, boxes):
        line_width = box[2] - box[0]
        draw.text(((width - line_width) // 2 - box[0], y - box[1]), line, font=font, fill=_hex_rgb(brand.SOFT_WHITE) + (255,))
        y += line_height + spacing
    image.save(path)
    return path


def render_cue_images(cues: Sequence[Cue], size: Tuple[int, int], out_dir: Path,
                      font_file: Optional[Path] = None) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    return [render_cue_image(cue, size, out_dir / f"cue_{index:04d}.png", font_file) for index, cue in enumerate(cues)]


def build_burn_command(ffmpeg: str, video: Path, images: Sequence[Path], cues: Sequence[Cue], output: Path) -> List[str]:
    command = [ffmpeg, "-y", "-v", "error", "-i", str(video)]
    for image in images:
        command += ["-i", str(image)]
    filters = []
    previous = "[0:v]"
    for index, cue in enumerate(cues, 1):
        label = f"[v{index}]"
        filters.append(f"{previous}[{index}:v]overlay=0:0:enable='between(t,{cue.start:.3f},{cue.end:.3f})'{label}")
        previous = label
    command += [
        "-filter_complex", ";".join(filters),
        "-map", previous, "-map", "0:a?",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "copy",
        str(output),
    ]
    return command


def burn_captions(
    video: Path, cues: Sequence[Cue], output: Path, quality: str = "low",
    run: Callable[..., subprocess.CompletedProcess] = subprocess.run,
    font_file: Optional[Path] = None,
) -> Path:
    if not cues:
        raise CaptionBurnError("cannot burn captions: there are no caption cues")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise CaptionBurnError("ffmpeg is missing; install it to burn in captions")
    size = VIDEO_SIZES[quality]
    with tempfile.TemporaryDirectory(prefix="ai_sankalp_captions_") as directory:
        images = render_cue_images(cues, size, Path(directory), font_file or brand.caption_font_file())
        process = run(build_burn_command(ffmpeg, video, images, cues, output), capture_output=True, text=True)
    if process.returncode != 0:
        tail = "\n".join(part for part in (process.stdout, process.stderr) if part)[-3000:]
        raise CaptionBurnError(f"ffmpeg could not burn captions into {Path(video).name}:\n{tail}")
    return output
