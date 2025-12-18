#!/bin/bash
set -e

echo "Installing system dependencies..."
# Assumes Debian/Ubuntu based system (Jetson Linux is based on Ubuntu)
sudo apt-get update
sudo apt-get install -y libsndfile1 portaudio19-dev ffmpeg curl jq

echo "Creating models directory..."
mkdir -p models

echo "Downloading Vosk model (small-en-us)..."
if [ ! -d "models/vosk-model-small-en-us-0.15" ]; then
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip -O models/vosk.zip
    unzip models/vosk.zip -d models/
    rm models/vosk.zip
else
    echo "Vosk model already exists."
fi

echo "Downloading Piper TTS..."
# Note: Using amd64 for potential testing in x86 environments.
# For Jetson Nano (aarch64), use the appropriate release, e.g., piper_linux_aarch64.tar.gz
# This script attempts to detect architecture.

ARCH=$(uname -m)
if [ "$ARCH" = "aarch64" ]; then
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_linux_aarch64.tar.gz"
else
    PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_linux_x86_64.tar.gz"
fi

if [ ! -d "piper" ]; then
    echo "Downloading Piper for $ARCH..."
    wget $PIPER_URL -O piper.tar.gz
    tar -xvf piper.tar.gz
    rm piper.tar.gz
else
    echo "Piper already installed."
fi

echo "Downloading Piper Voice (Amy Medium)..."
if [ ! -f "models/en_US-amy-medium.onnx" ]; then
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx -O models/en_US-amy-medium.onnx
    wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/amy/medium/en_US-amy-medium.onnx.json -O models/en_US-amy-medium.onnx.json
else
    echo "Piper voice already exists."
fi

echo "Setup complete. Please ensure Ollama is installed and 'ollama pull qwen2.5:0.5b' has been run."
