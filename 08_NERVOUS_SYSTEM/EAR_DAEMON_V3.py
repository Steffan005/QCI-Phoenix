import time
import json
import requests
import os
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import webrtcvad
import collections
import sys
from datetime import datetime

# Configuration
LOG_FILE = "/tmp/ear_daemon.log"
SPEECH_FILE = "/tmp/unity_speech.txt"
INTERRUPT_FILE = "/tmp/unity_interrupt.signal"
EAR_CONFIG = "/tmp/ear_config.json"
UNITY_BACKEND_URL = "http://127.0.0.1:8000"

# Audio Settings
SAMPLE_RATE = 16000
FRAME_DURATION_MS = 30
FRAME_SIZE = int(SAMPLE_RATE * FRAME_DURATION_MS / 1000)
VAD_AGGRESSIVENESS = 3 

def load_config():
    if os.path.exists(EAR_CONFIG):
        try:
            with open(EAR_CONFIG, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"threshold": 3000, "interrupt": True}

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    # print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

class VADAudio(object):
    """Filter & Segment audio with Voice Activity Detection."""
    def __init__(self, aggressiveness=3, device=None, input_rate=None, file=None):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.sample_rate = SAMPLE_RATE
        self.block_size = FRAME_SIZE
        self.block_size_bytes = int(2 * self.block_size) # 16-bit = 2 bytes

    def frame_generator(self):
        """Generator that yields all audio frames from microphone."""
        if self.input_rate == self.sample_rate:
            result = self.read()
            while True:
                yield result
                result = self.read()
        else:
            raise Exception("Resampling not implemented")

    def read(self):
        """Read a block of audio data."""
        return sys.stdin.read(self.block_size_bytes)

    def vad_collector(self, sample_rate, frame_duration_ms, padding_duration_ms, vad, frames):
        """Filters out non-voiced audio frames."""
        num_padding_frames = int(padding_duration_ms / frame_duration_ms)
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False
        
        voiced_frames = []
        
        for frame in frames:
            is_speech = vad.is_speech(frame, sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > 0.9 * ring_buffer.maxlen:
                    triggered = True
                    # We found speech! Trigger interrupt immediately.
                    trigger_interrupt()
                    
                    for f, s in ring_buffer:
                        voiced_frames.append(f)
                    ring_buffer.clear()
            else:
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > 0.9 * ring_buffer.maxlen:
                    triggered = False
                    yield b''.join(voiced_frames)
                    ring_buffer.clear()
                    voiced_frames = []

def trigger_interrupt():
    """Signal the Larynx to shut up."""
    # Only trigger if file doesn't exist (debounce)
    if not os.path.exists(INTERRUPT_FILE):
        with open(INTERRUPT_FILE, "w") as f:
            f.write("STOP")
        log("    >>> VAD DETECTED SPEECH - INTERRUPT TRIGGERED")

def send_to_brain(text):
    """Send transcribed text to Unity Brain."""
    log(f"    Sending to Brain: {text}")
    try:
        payload = {"message": text}
        response = requests.post(f"{UNITY_BACKEND_URL}/orchestrator/chat", json=payload, timeout=30)
        if response.status_code == 200:
            reply = response.json().get("response", "I heard you.")
            return reply
        else:
            return f"Brain Error: {response.status_code}"
    except Exception as e:
        return f"Connection Error: {e}"

def listen_and_transcribe_robust():
    """Use SpeechRecognition with tuned parameters for robustness."""
    config = load_config()
    target_threshold = config.get("threshold", 3000)
    interrupt_enabled = config.get("interrupt", True)
    
    recognizer = sr.Recognizer()
    
    # CRITICAL: Disable dynamic thresholding to prevent adapting to silence
    recognizer.dynamic_energy_threshold = False
    recognizer.energy_threshold = target_threshold
    
    with sr.Microphone(sample_rate=SAMPLE_RATE) as source:
        # We skip calibration if we trust the config
        # log("    Calibrating background noise (1s)...")
        # recognizer.adjust_for_ambient_noise(source, duration=1)
        
        log(f"    Listening (Threshold: {target_threshold})...")
        
        try:
            # Listen
            audio = recognizer.listen(source, timeout=None, phrase_time_limit=10)
            
            # If we got here, energy threshold was crossed.
            if interrupt_enabled:
                trigger_interrupt()
            
            log("    Processing audio...")
            text = recognizer.recognize_google(audio)
            log(f"    Heard: '{text}'")
            return text
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            log(f"    Recognition Error: {e}")
            return None

def main():
    log("⟨⦿⟩ EAR DAEMON V3 ACTIVATED")
    log("    Mode: ROBUST ENERGY THRESHOLD")
    
    while True:
        try:
            text = listen_and_transcribe_robust()
            
            if text:
                response = send_to_brain(text)
                
                log(f"    Unity Says: {response[:50]}...")
                with open(SPEECH_FILE, "w") as f:
                    f.write(response)
                
                time.sleep(0.5)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"Loop Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
