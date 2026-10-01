"""Speech-service selection shared by every visual template."""
from __future__ import annotations

from pathlib import Path

from .models import VoiceoverConfig

AUDIO_CACHE_DIRS = {"gtts": "audio", "edge": "audio_edge"}


def audio_cache_dir(voiceover: VoiceoverConfig, project_root: Path) -> Path:
    return Path(project_root) / "generated" / AUDIO_CACHE_DIRS[voiceover.provider]


def build_speech_service(voiceover: VoiceoverConfig, project_root: Path):
    """Return the manim-voiceover service for `voiceover.provider`.

    gTTS caches under generated/audio and Edge TTS under generated/audio_edge.
    Neither constructor touches the network; audio is fetched at render time.
    """
    cache_dir = audio_cache_dir(voiceover, project_root)
    if voiceover.provider == "edge":
        from .edge_tts_service import EdgeTTSService

        return EdgeTTSService(
            voice=voiceover.voice,
            rate=voiceover.rate,
            pitch=voiceover.pitch,
            global_speed=voiceover.speed,
            cache_dir=cache_dir,
        )
    from manim_voiceover.services.gtts import GTTSService

    return GTTSService(
        lang=voiceover.language,
        tld=voiceover.tld,
        global_speed=voiceover.speed,
        cache_dir=cache_dir,
    )
