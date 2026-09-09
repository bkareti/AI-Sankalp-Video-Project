from __future__ import annotations

from pathlib import Path

from edge_tts import Communicate
from manim_voiceover.helper import remove_bookmarks
from manim_voiceover.services.base import SpeechService


class EdgeTTSService(SpeechService):
    """Natural Microsoft Edge neural speech for Manim Voiceover."""

    def __init__(
        self,
        voice: str = "en-IN-NeerjaNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
        volume: str = "+0%",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.voice = voice
        self.rate = rate
        self.pitch = pitch
        self.volume = volume

    def generate_from_text(self, text: str, cache_dir=None, path=None, **kwargs) -> dict:
        cache_dir = Path(cache_dir or self.cache_dir)
        input_text = remove_bookmarks(text)
        input_data = {
            "input_text": input_text,
            "service": "edge_tts",
            "voice": self.voice,
            "rate": self.rate,
            "pitch": self.pitch,
            "volume": self.volume,
        }
        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result

        audio_path = path or f"{self.get_audio_basename(input_data)}.mp3"
        Communicate(
            input_text,
            voice=self.voice,
            rate=self.rate,
            pitch=self.pitch,
            volume=self.volume,
        ).save_sync(str(cache_dir / audio_path))
        return {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }
