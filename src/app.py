import streamlit as st
import threading
import time
import os
import json
import queue
from src.modules.audio import AudioRecorder, WakeWordListener
from src.modules.stt import transcribe_audio
from src.modules.llm import generate_medical_note
from src.modules.tts import speak_text
from src.utils.memory import cleanup_resources

# --- Singleton Logic for Background Listener ---

@st.cache_resource
def get_command_queue():
    return queue.Queue()

@st.cache_resource
def get_listener_state():
    return {"running": False, "thread": None, "pause_event": threading.Event()}

command_queue = get_command_queue()
listener_state = get_listener_state()

def listener_callback(text):
    print(f"Heard: {text}")
    keywords = ["scribe", "stop", "next patient", "subjective", "objective", "assessment", "plan", "codes"]
    for k in keywords:
        if k in text.lower():
            command_queue.put(k)

def start_background_listener():
    if not listener_state["running"]:
        listener_state["running"] = True

        def run():
            listener = WakeWordListener()
            listener.start_listening(callback=listener_callback, pause_event=listener_state["pause_event"])

        t = threading.Thread(target=run, daemon=True)
        listener_state["thread"] = t
        t.start()

# --- Main App ---

st.set_page_config(layout="wide", page_title="AI Medical Scribe")

# Start background thread
start_background_listener()

# Initialize session state
if 'state' not in st.session_state:
    st.session_state['state'] = 'IDLE'
if 'recorder' not in st.session_state:
    st.session_state['recorder'] = AudioRecorder()
if 'patient_data' not in st.session_state:
    st.session_state['patient_data'] = {}
if 'transcription' not in st.session_state:
    st.session_state['transcription'] = ""

# Sidebar
st.sidebar.title("Controls")
status_placeholder = st.sidebar.empty()

def update_status(status):
    status_placeholder.markdown(f"**Status:** {status}")

st.title("AI Medical Scribe (Jetson Nano Edition)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Live Transcription / Input")
    transcription_display = st.empty()
    if st.session_state['transcription']:
        transcription_display.text_area("Transcription", st.session_state['transcription'], height=200)

with col2:
    st.subheader("Structured Medical Note")
    json_display = st.empty()
    if st.session_state['patient_data']:
        json_display.json(st.session_state['patient_data'])

# --- Helper Functions ---

def run_pipeline():
    cleanup_resources()
    filename = "recording.wav"
    if os.path.exists(filename):
        text = transcribe_audio(filename, model_size='tiny', device='cpu')
        st.session_state['transcription'] = text
        cleanup_resources()

        update_status("Processing... (Ollama LLM)")
        data = generate_medical_note(text)
        st.session_state['patient_data'] = data
        cleanup_resources()

        st.session_state['state'] = 'REVIEW'
        update_status("Review Mode")
        st.rerun()
    else:
        st.error("Recording file not found.")
        st.session_state['state'] = 'IDLE'
        st.rerun()

# --- Event Loop / State Machine ---

# Check for voice commands
try:
    while not command_queue.empty():
        cmd = command_queue.get_nowait()
        st.toast(f"Voice Command: {cmd}")

        if cmd == "scribe":
            if st.session_state['state'] == 'IDLE':
                # Pause listener to avoid conflict with recorder
                listener_state["pause_event"].set()

                st.session_state['state'] = 'RECORDING'
                st.session_state['recorder'].start_recording()
                st.rerun()

        elif cmd == "stop":
            if st.session_state['state'] == 'RECORDING':
                st.session_state['recorder'].stop_recording()

                # Resume listener
                listener_state["pause_event"].clear()

                run_pipeline()

        elif cmd == "next patient":
            st.session_state['state'] = 'IDLE'
            st.session_state['patient_data'] = {}
            st.session_state['transcription'] = ""
            cleanup_resources()
            st.rerun()

        # Review Mode Commands
        elif st.session_state['state'] == 'REVIEW':
            data = st.session_state['patient_data']
            if "subjective" in cmd:
                speak_text(data.get('subjective', 'No subjective data.'))
            elif "objective" in cmd:
                speak_text(data.get('objective', 'No objective data.'))
            elif "assessment" in cmd:
                speak_text(data.get('assessment', 'No assessment data.'))
            elif "plan" in cmd:
                speak_text(data.get('plan', 'No plan data.'))
            elif "codes" in cmd:
                codes = data.get('icd_codes', [])
                speak_text(f"ICD Codes: {', '.join(codes) if isinstance(codes, list) else codes}")

except queue.Empty:
    pass


# UI Logic based on State
if st.session_state['state'] == 'IDLE':
    update_status("IDLE (Say 'Scribe' to start)")
    if st.button("Start Recording"):
        # Pause listener to avoid conflict with recorder
        listener_state["pause_event"].set()

        st.session_state['state'] = 'RECORDING'
        st.session_state['recorder'].start_recording()
        st.rerun()

elif st.session_state['state'] == 'RECORDING':
    update_status("RECORDING... (Say 'Stop' to finish)")
    if st.button("Stop Recording"):
        st.session_state['recorder'].stop_recording()

        # Resume listener
        listener_state["pause_event"].clear()

        run_pipeline()

elif st.session_state['state'] == 'PROCESSING':
    update_status("Processing...")

elif st.session_state['state'] == 'REVIEW':
    update_status("REVIEW (Say 'Next Patient' to reset)")

    st.write("### Voice Commands")
    st.info("Say 'Subjective', 'Objective', 'Assessment', 'Plan', or 'Codes' to read that section.")

    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("Read Subjective"):
        speak_text(st.session_state['patient_data'].get('subjective', 'No subjective data.'))
    if c2.button("Read Objective"):
        speak_text(st.session_state['patient_data'].get('objective', 'No objective data.'))
    if c3.button("Read Assessment"):
        speak_text(st.session_state['patient_data'].get('assessment', 'No assessment data.'))
    if c4.button("Read Plan"):
        speak_text(st.session_state['patient_data'].get('plan', 'No plan data.'))
    if c5.button("Read Codes"):
        codes = st.session_state['patient_data'].get('icd_codes', [])
        speak_text(f"ICD Codes: {', '.join(codes) if isinstance(codes, list) else codes}")

    if st.button("Next Patient (Reset)"):
        st.session_state['state'] = 'IDLE'
        st.session_state['patient_data'] = {}
        st.session_state['transcription'] = ""
        cleanup_resources()
        st.rerun()

if st.session_state['state'] in ['IDLE', 'RECORDING', 'REVIEW']:
    time.sleep(1)
    st.rerun()
