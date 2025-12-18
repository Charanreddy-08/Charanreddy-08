# AI Medical Scribe (Jetson Nano Edition)

A voice-controlled AI Medical Scribe application optimized for the NVIDIA Jetson Nano (4GB). It captures patient observations, transcribes them, generates structured medical notes using an LLM, and provides interactive voice retrieval.

## Hardware Requirements
- **Device**: NVIDIA Jetson Nano (4GB Shared RAM/VRAM).
- **Microphone**: USB Microphone or other audio input device.
- **Speaker**: Audio output device for TTS feedback.

## Prerequisites
1. **Ollama**: Ensure Ollama is installed and running.
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```
2. **Pull the LLM Model**:
   The application uses `qwen2.5:0.5b` for low memory footprint.
   ```bash
   ollama pull qwen2.5:0.5b
   ```

## Installation

1. **Clone the repository** (if not already done).

2. **Install System Dependencies & Download Models**:
   Run the setup script to install `libsndfile`, `portaudio`, `ffmpeg`, and download the required Vosk and Piper models.
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Install Python Dependencies**:
   It is recommended to use a virtual environment.
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

To start the Scribe dashboard:

```bash
streamlit run src/app.py
```

For **headless operation** (running on Jetson, viewing on laptop):
The terminal will display a network URL (e.g., `http://192.168.1.X:8501`). Open this URL in your web browser.

## Usage Guide

### 1. Idle State
- **Voice Command**: Say **"Scribe"** to start recording.
- **Manual Control**: Click "Start Recording" button.

### 2. Recording
- Speak your patient observations.
- **Voice Command**: Say **"Stop"** to finish recording and begin processing.
- **Manual Control**: Click "Stop Recording" button.

### 3. Processing
- The system will:
  1. Transcribe audio (Whisper on CPU).
  2. Generate structured notes (Ollama on GPU).
  3. Clean up memory aggressively between steps.

### 4. Review Mode
- The structured JSON note is displayed.
- **Voice Commands**:
  - **"Subjective"**: Reads the Subjective section.
  - **"Objective"**: Reads the Objective section.
  - **"Assessment"**: Reads the Assessment section.
  - **"Plan"**: Reads the Plan section.
  - **"Codes"**: Reads the ICD Codes.
- **Reset**:
  - Say **"Next Patient"** to clear data and return to Idle state.
