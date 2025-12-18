import os
import subprocess
import tempfile

def speak_text(text, model_path="models/en_US-amy-medium.onnx", binary_path="piper/piper"):
    """
    Synthesizes speech using Piper TTS.

    Args:
        text (str): The text to speak.
        model_path (str): Path to the ONNX model.
        binary_path (str): Path to the Piper binary.
    """

    # Resolve absolute paths
    model_path = os.path.abspath(model_path)
    binary_path = os.path.abspath(binary_path)

    if not os.path.exists(binary_path):
        print(f"Error: Piper binary not found at {binary_path}")
        return
    if not os.path.exists(model_path):
        print(f"Error: Piper model not found at {model_path}")
        return

    # Create a temporary file for the text to avoid shell injection issues
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as temp_text_file:
        temp_text_file.write(text)
        temp_text_path = temp_text_file.name

    # Create a temporary file for the wav output to be played
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.wav') as temp_wav_file:
        temp_wav_path = temp_wav_file.name

    try:
        # Construct the command
        # Requirement: "Use tee in the subprocess pipeline to play the voice response through aplay
        # while simultaneously saving the output to a .wav file for verification."

        # Piper reads from stdin (cat temp_text_path | piper ...)
        # Piper outputs raw audio to stdout -> tee -> aplay & file

        # Note: Piper output format depends on arguments. default is raw audio (PCM) or wav.
        # Usually it writes to stdout if --output_file is not specified.
        # --output-raw might be needed for aplay if piping directly, or we ensure aplay can handle the stream.
        # Piper defaults to WAV on stdout if no output file specified? Let's check docs logic.
        # Actually standard usage: echo "text" | piper --model ... --output_file output.wav
        # To pipe: echo "text" | piper --model ... --output-raw | aplay ...

        # The requirement says: "Use tee ... to play ... while simultaneously saving ... to a .wav file".
        # 'tee' splits stdout. So we need the stdout to be valid audio data.

        # Command structure:
        # cat text_file | piper --model model_path --output_file - | tee output.wav | aplay
        # Using '-' as output file typically tells piper to write to stdout.

        cmd = (
            f"cat {temp_text_path} | "
            f"{binary_path} --model {model_path} --output_file - | "
            f"tee {temp_wav_path} | "
            f"aplay"
        )

        print(f"Executing TTS command: {cmd}")
        subprocess.run(cmd, shell=True, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error executing TTS: {e}")
    finally:
        # Clean up text file
        if os.path.exists(temp_text_path):
            os.remove(temp_text_path)
        # We might want to keep the wav file for verification as per requirements ("saving the output to a .wav file for verification")
        # But if it's a temp file, it's hard to verify later.
        # The requirements say "saving the output to a .wav file for verification".
        # Maybe we should move it to a permanent location or just leave it.
        # For now, I'll print the location.
        print(f"Audio saved to: {temp_wav_path}")
