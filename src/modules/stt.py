import whisper
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

def transcribe_audio(audio_path, model_size='tiny', device='cpu'):
    """
    Transcribes audio using OpenAI Whisper.
    Forces CPU execution to save GPU for LLM.

    Args:
        audio_path (str): Path to the audio file.
        model_size (str): Whisper model size ('tiny', 'base', etc.).
        device (str): Device to run on ('cpu' or 'cuda'). Defaults to 'cpu'.

    Returns:
        str: Transcribed text.
    """
    print(f"Loading Whisper model ({model_size}) on {device}...")
    try:
        model = whisper.load_model(model_size, device=device)

        print(f"Transcribing {audio_path}...")
        result = model.transcribe(audio_path, fp16=False) # fp16=False is often needed for CPU or older GPUs

        text = result['text'].strip()
        print(f"Transcription complete: {text[:50]}...")
        return text
    except Exception as e:
        print(f"Error during transcription: {e}")
        return ""
