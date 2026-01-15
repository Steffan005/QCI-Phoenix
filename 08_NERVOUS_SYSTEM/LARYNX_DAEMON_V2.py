import time
import json
import requests
import os
import sounddevice as sd
import soundfile as sf
import io
import threading
from datetime import datetime

# Configuration
SPEECH_FILE = "/tmp/unity_speech.txt"
INTERRUPT_FILE = "/tmp/unity_interrupt.signal"
LOG_FILE = "/tmp/larynx_daemon.log"
LARYNX_CONFIG = "/tmp/larynx_config.json"
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "sk_1fa8403d01ec4589a0dbe28c5ceac586165476b6395ff66c")
VOICE_ID = "cjVigY5qzO86Huf0OWal" # Eric
MODEL_ID = "eleven_monolingual_v1"

# Global state for interruption
current_stream = None
stop_event = threading.Event()

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    # print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def check_interrupt():
    """Check if interrupt signal exists."""
    if os.path.exists(INTERRUPT_FILE):
        log("    >>> INTERRUPT SIGNAL RECEIVED")
        stop_event.set()
        sd.stop() # Kill audio immediately
        try:
            os.remove(INTERRUPT_FILE)
        except:
            pass
        return True
    return False

def play_audio(data, samplerate):
    """Play audio with interrupt support."""
    stop_event.clear()
    
    # Start playback in a non-blocking way
    sd.play(data, samplerate)
    
    # Wait loop to check for interrupts
    duration = len(data) / samplerate
    start_time = time.time()
    
    while time.time() - start_time < duration:
        if check_interrupt():
            return # Stop immediately
        time.sleep(0.1)
    
    sd.wait() # Ensure it finished if not interrupted

def load_config():
    if os.path.exists(LARYNX_CONFIG):
        try:
            with open(LARYNX_CONFIG, 'r') as f:
                return json.load(f)
        except: pass
    return {"volume": 1.0, "speed": 1.0}

def speak_fallback(text):
    """Fallback to macOS 'say' command."""
    config = load_config()
    rate = int(175 * config.get("speed", 1.0)) # Normal rate is ~175
    
    log(f"    Using Fallback TTS (Rate: {rate}): {text[:50]}...")
    # Escape quotes
    safe_text = text.replace('"', '\\"')
    os.system(f'say -r {rate} "{safe_text}"')

def speak_text(text):
    """Send text to ElevenLabs and play audio."""
    if not text:
        return

    log(f"Speaking: {text[:50]}...")
    
    # Check interrupt before even starting
    if check_interrupt():
        return

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVENLABS_API_KEY
    }
    data = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            audio_data = io.BytesIO(response.content)
            data, samplerate = sf.read(audio_data)
            play_audio(data, samplerate)
            log("    Audio playback complete.")
        else:
            log(f"    ElevenLabs Error: {response.status_code}")
            speak_fallback(text)
    except Exception as e:
        log(f"    Speech Error: {e}")
        speak_fallback(text)

def main():
    log("⟨⦿⟩ LARYNX DAEMON V2 ACTIVATED")
    log("    Interruptibility: ENABLED")
    
    # Clear files
    if os.path.exists(SPEECH_FILE): os.remove(SPEECH_FILE)
    if os.path.exists(INTERRUPT_FILE): os.remove(INTERRUPT_FILE)
    
    while True:
        try:
            # Check for speech
            if os.path.exists(SPEECH_FILE):
                with open(SPEECH_FILE, "r") as f:
                    text = f.read().strip()
                
                # Remove file immediately so we don't loop
                os.remove(SPEECH_FILE)
                
                if text:
                    speak_text(text)
            
            # Check for interrupt (just in case)
            check_interrupt()
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            log(f"Loop Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
