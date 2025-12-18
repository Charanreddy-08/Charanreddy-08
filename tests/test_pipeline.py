import unittest
from unittest.mock import patch, MagicMock
import os
import json
import sys

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.modules.stt import transcribe_audio
from src.modules.llm import generate_medical_note
from src.modules.tts import speak_text

class TestPipeline(unittest.TestCase):

    @patch('src.modules.stt.whisper')
    def test_transcribe_audio(self, mock_whisper):
        # Mocking whisper
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model
        mock_model.transcribe.return_value = {'text': "Patient complains of headache."}

        result = transcribe_audio("dummy.wav")
        self.assertEqual(result, "Patient complains of headache.")
        mock_whisper.load_model.assert_called_with('tiny', device='cpu')

    @patch('src.modules.llm.ollama')
    def test_generate_medical_note(self, mock_ollama):
        # Mocking ollama
        mock_response = {
            'message': {
                'content': json.dumps({
                    "subjective": "Headache",
                    "objective": "High BP",
                    "assessment": "Migraine",
                    "plan": "Rest",
                    "icd_codes": ["G43.9"]
                })
            }
        }
        mock_ollama.chat.return_value = mock_response

        result = generate_medical_note("Patient complains of headache.")

        self.assertEqual(result['subjective'], "Headache")
        self.assertIn("icd_codes", result)
        mock_ollama.chat.assert_called()
        # Verify keep_alive=0
        args, kwargs = mock_ollama.chat.call_args
        self.assertEqual(kwargs['keep_alive'], 0)

    @patch('subprocess.run')
    def test_speak_text(self, mock_run):
        # Mock file existence
        with patch('os.path.exists', return_value=True):
            speak_text("Hello World")

            # Check if subprocess was called
            self.assertTrue(mock_run.called)
            cmd = mock_run.call_args[0][0]
            self.assertIn("piper", cmd)
            self.assertIn("tee", cmd)
            self.assertIn("aplay", cmd)

if __name__ == '__main__':
    unittest.main()
