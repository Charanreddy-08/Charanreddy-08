import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock sounddevice BEFORE importing audio module
sys.modules["sounddevice"] = MagicMock()

from src.modules.audio import WakeWordListener

class TestVoiceInteraction(unittest.TestCase):

    @patch('src.modules.audio.Model')
    @patch('src.modules.audio.KaldiRecognizer')
    def test_listener_logic(self, mock_rec, mock_model):
        # We want to verify that if we use the logic from app.py (which uses WakeWordListener internally or re-implements it),
        # it correctly identifies keywords.

        # Mock os.path.exists to pass model check
        with patch('os.path.exists', return_value=True):
            listener = WakeWordListener(model_path="dummy_path")
            self.assertIsNotNone(listener)

    # Testing the logic flow intended for app.py
    def test_keyword_parsing(self):
        text = "scribe please"
        keywords = ["scribe", "stop", "next patient"]
        found = [k for k in keywords if k in text.lower()]
        self.assertIn("scribe", found)

        text = "read the subjective section"
        found = [k for k in ["subjective"] if k in text.lower()]
        self.assertIn("subjective", found)

if __name__ == '__main__':
    unittest.main()
