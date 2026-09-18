import asyncio
import importlib.util
from pathlib import Path
import tempfile
import unittest

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
TTS_BUILD = ROOT / "template" / "scripts" / "tts_build.py"


def load_tts_build():
    spec = importlib.util.spec_from_file_location("a2e_tts_build", TTS_BUILD)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RussianLanguageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tts = load_tts_build()

    def test_detect_lang_recognizes_russian_cyrillic(self):
        items = [
            {"type": "chapter", "title": "Введение"},
            {"type": "sent", "raw": "ИИ-агент берёт на себя повторяющиеся задачи."},
        ]
        self.assertEqual(self.tts.detect_lang(items), "ru")

    def test_text_em_uses_cyrillic_glyph_widths(self):
        self.assertAlmostEqual(self.tts.text_em("Привет"), 3.443, delta=0.08)

    def test_russian_has_a_single_line_subtitle_budget(self):
        self.assertEqual(self.tts.SUB_BUDGET.get("ru"), "40 знаков")

    def test_auto_mode_selects_russian_edge_voice_and_space_separator(self):
        tts = load_tts_build()

        async def fake_synth_sentence(chunks, sep=""):
            self.assertEqual(sep, " ")
            return np.zeros(4800, dtype=np.float32), [0.0], 0.1

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "script").mkdir()
            (root / "src" / "common").mkdir(parents=True)
            narration = root / "script" / "narration.txt"
            narration.write_text("# CHAPTER 1 Введение\nРусский текст для проверки.\n", encoding="utf-8")
            setattr(tts, "ROOT", str(root))
            setattr(tts, "REM", str(root))
            setattr(tts, "SLUG", "test")
            setattr(tts, "CFG_LANG", "ru")
            setattr(tts, "ENGINE", "auto")
            setattr(tts, "synth_sentence", fake_synth_sentence)
            asyncio.run(tts.main(str(narration)))

        self.assertEqual(tts.ENGINE, "edge")
        self.assertEqual(tts.VOICE, "ru-RU-DmitryNeural")
        self.assertEqual(tts.RATE, "+0%")


if __name__ == "__main__":
    unittest.main()
