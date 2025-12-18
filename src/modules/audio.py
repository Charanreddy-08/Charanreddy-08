import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import queue
import json
import os
from vosk import Model, KaldiRecognizer
import sys

# Audio configuration
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = 'int16'

class AudioRecorder:
    def __init__(self, sample_rate=SAMPLE_RATE, channels=CHANNELS):
        self.sample_rate = sample_rate
        self.channels = channels
        self.recording = False
        self.frames = []

    def start_recording(self):
        self.recording = True
        self.frames = []
        print("Recording started...")
        # Start the input stream
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype=DTYPE,
            callback=self._callback
        )
        self.stream.start()

    def _callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        if self.recording:
            self.frames.append(indata.copy())

    def stop_recording(self, output_filename="recording.wav"):
        self.recording = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

        print("Recording stopped.")
        if not self.frames:
            print("No audio recorded.")
            return None

        # Concatenate frames
        audio_data = np.concatenate(self.frames, axis=0)

        # Save to WAV file
        wav.write(output_filename, self.sample_rate, audio_data)
        print(f"Audio saved to {output_filename}")
        return output_filename

class WakeWordListener:
    def __init__(self, model_path="models/vosk-model-small-en-us-0.15"):
        self.model_path = model_path
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Vosk model not found at {self.model_path}")

        # Suppress stderr to avoid ALSA spam
        self.model = Model(self.model_path)
        self.rec = None # Initialize lazily or re-use
        self.running = False

    def start_listening(self, callback, pause_event=None):
        """
        Continuously listens and calls the callback with recognized text.

        Args:
            callback (function): Function to call with recognized text.
            pause_event (threading.Event): If set, listening pauses.
        """
        self.running = True
        self.rec = KaldiRecognizer(self.model, SAMPLE_RATE)

        print("Starting continuous listening...")

        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype=DTYPE,
                               channels=CHANNELS) as stream:
            while self.running:
                # Check pause event
                if pause_event and pause_event.is_set():
                    # Sleep briefly to avoid busy loop while paused
                    import time
                    time.sleep(0.1)
                    continue

                try:
                    data, overflowed = stream.read(8000)
                    if self.rec.AcceptWaveform(bytes(data)):
                        result = json.loads(self.rec.Result())
                        text = result.get("text", "")
                        if text:
                            callback(text)
                except Exception as e:
                    print(f"Error in listener stream: {e}")
                    break

    def stop(self):
        self.running = False
