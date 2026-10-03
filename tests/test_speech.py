import tempfile
import unittest
from pathlib import Path

from ai_sankalp.models import VoiceoverConfig
from ai_sankalp.speech import audio_cache_dir, build_speech_service


class SpeechServiceTests(unittest.TestCase):
    def test_provider_selects_service_and_cache_dir(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            edge = VoiceoverConfig.from_dict({"provider": "edge", "rate": "-4%", "pitch": "+1Hz"})
            service = build_speech_service(edge, root)
            self.assertEqual("EdgeTTSService", type(service).__name__)
            self.assertEqual("-4%", service.rate)
            self.assertEqual(root / "generated" / "audio_edge", audio_cache_dir(edge, root))

            gtts = VoiceoverConfig.from_dict({"provider": "gtts", "tld": "co.in"})
            service = build_speech_service(gtts, root)
            self.assertEqual("GTTSService", type(service).__name__)
            self.assertEqual(root / "generated" / "audio", audio_cache_dir(gtts, root))


if __name__ == "__main__":
    unittest.main()
