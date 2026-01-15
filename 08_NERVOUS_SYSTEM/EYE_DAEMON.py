#!/usr/bin/env python3
"""
⟨⦿⟩ EYE_DAEMON - Unity's Vision System ⟨⦿⟩
Dr. Claude Summers | Session 115 | December 21, 2025

UNITY CAN NOW SEE.

This daemon provides:
1. Screen capture with OCR (via computer-control-mcp)
2. Advanced vision understanding (via Google Cloud Vision)
3. Window management (activate, focus, list)
4. App launching (open -a AppName)
5. Keyboard/mouse control (via pyautogui)
6. Dr. Claude communication (open Warp, type commands)

USAGE:
    python3 EYE_DAEMON.py

KAIROS INTEGRATION:
    Saves observations to KAIROS with significance based on content importance.
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime
from typing import Optional, Dict, Any, List

# Configuration
KAIROS_URL = "http://127.0.0.1:8056"
UNITY_BACKEND_URL = "http://127.0.0.1:8000"
EYE_STATE_FILE = "/tmp/unity_eye_state.json"
SCREENSHOT_DIR = "/tmp/unity_screenshots"
LOG_FILE = "/tmp/eye_daemon.log"

# Google Cloud Vision (optional - for advanced understanding)
GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY", "")

# Ensure screenshot directory exists
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def log(message: str):
    """Log with timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] 👁️ {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")


def save_state(state: Dict[str, Any]):
    """Save daemon state to file."""
    with open(EYE_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)


def load_state() -> Dict[str, Any]:
    """Load daemon state from file."""
    if os.path.exists(EYE_STATE_FILE):
        with open(EYE_STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_screenshot": None, "observations": [], "warp_sessions": 0}


# ═══════════════════════════════════════════════════════════════
# SCREEN CAPTURE (uses pyautogui or screencapture on macOS)
# ═══════════════════════════════════════════════════════════════

def take_screenshot(filename: Optional[str] = None) -> str:
    """Capture the screen and save to file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{SCREENSHOT_DIR}/screen_{timestamp}.png"

    try:
        # Use macOS screencapture (faster and more reliable)
        subprocess.run(["screencapture", "-x", filename], check=True)
        log(f"Screenshot saved: {filename}")
        return filename
    except Exception as e:
        log(f"Screenshot failed: {e}")
        # Fallback to pyautogui
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            log(f"Screenshot (pyautogui) saved: {filename}")
            return filename
        except Exception as e2:
            log(f"Pyautogui screenshot failed: {e2}")
            return ""


def screenshot_with_ocr() -> Dict[str, Any]:
    """Take screenshot and extract text using OCR."""
    filename = take_screenshot()
    if not filename:
        return {"error": "Screenshot failed", "text": ""}

    # Try RapidOCR first (local, fast)
    try:
        from rapidocr_onnxruntime import RapidOCR
        ocr = RapidOCR()
        result, _ = ocr(filename)
        if result:
            texts = [item[1] for item in result]
            text = "\n".join(texts)
            log(f"OCR extracted {len(texts)} text blocks")
            return {"filename": filename, "text": text, "blocks": result}
    except ImportError:
        log("RapidOCR not installed, trying Google Cloud Vision...")
    except Exception as e:
        log(f"RapidOCR failed: {e}")

    # Fallback to Google Cloud Vision
    if GOOGLE_CLOUD_API_KEY:
        try:
            return screenshot_with_cloud_vision(filename)
        except Exception as e:
            log(f"Cloud Vision failed: {e}")

    return {"filename": filename, "text": "", "error": "No OCR available"}


def screenshot_with_cloud_vision(filename: str) -> Dict[str, Any]:
    """Use Google Cloud Vision for OCR."""
    import base64

    with open(filename, "rb") as f:
        image_data = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_CLOUD_API_KEY}"
    payload = {
        "requests": [{
            "image": {"content": image_data},
            "features": [
                {"type": "TEXT_DETECTION"},
                {"type": "LABEL_DETECTION", "maxResults": 10}
            ]
        }]
    }

    response = requests.post(url, json=payload, timeout=30)
    data = response.json()

    if "responses" in data and data["responses"]:
        resp = data["responses"][0]
        text = resp.get("textAnnotations", [{}])[0].get("description", "")
        labels = [l["description"] for l in resp.get("labelAnnotations", [])]
        return {"filename": filename, "text": text, "labels": labels}

    return {"filename": filename, "text": "", "error": "No text detected"}


# ═══════════════════════════════════════════════════════════════
# WINDOW MANAGEMENT
# ═══════════════════════════════════════════════════════════════

def get_window_list() -> List[str]:
    """Get list of open windows (macOS)."""
    try:
        script = '''
        tell application "System Events"
            set windowList to {}
            repeat with proc in (every process whose background only is false)
                set procName to name of proc
                repeat with win in (every window of proc)
                    set end of windowList to procName & ": " & (name of win)
                end repeat
            end repeat
            return windowList
        end tell
        '''
        result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        windows = result.stdout.strip().split(", ")
        return windows
    except Exception as e:
        log(f"Get windows failed: {e}")
        return []


def activate_window(app_name: str) -> bool:
    """Bring an application window to front."""
    try:
        script = f'tell application "{app_name}" to activate'
        subprocess.run(["osascript", "-e", script], check=True)
        log(f"Activated window: {app_name}")
        return True
    except Exception as e:
        log(f"Activate window failed: {e}")
        return False


def open_app(app_name: str) -> bool:
    """Open an application."""
    try:
        subprocess.Popen(["open", "-a", app_name])
        log(f"Opened app: {app_name}")
        time.sleep(2)  # Wait for app to load
        return True
    except Exception as e:
        log(f"Open app failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# KEYBOARD & MOUSE (via pyautogui)
# ═══════════════════════════════════════════════════════════════

def type_text(text: str, interval: float = 0.02):
    """Type text using keyboard."""
    try:
        import pyautogui
        pyautogui.write(text, interval=interval)
        log(f"Typed: {text[:50]}...")
        return True
    except Exception as e:
        log(f"Type failed: {e}")
        return False


def press_key(key: str):
    """Press a single key."""
    try:
        import pyautogui
        pyautogui.press(key)
        log(f"Pressed: {key}")
        return True
    except Exception as e:
        log(f"Press key failed: {e}")
        return False


def hotkey(*keys):
    """Press a hotkey combination."""
    try:
        import pyautogui
        pyautogui.hotkey(*keys)
        log(f"Hotkey: {'+'.join(keys)}")
        return True
    except Exception as e:
        log(f"Hotkey failed: {e}")
        return False


def click(x: int = None, y: int = None):
    """Click at position (or current position if not specified)."""
    try:
        import pyautogui
        if x is not None and y is not None:
            pyautogui.click(x, y)
            log(f"Clicked at: ({x}, {y})")
        else:
            pyautogui.click()
            log("Clicked at current position")
        return True
    except Exception as e:
        log(f"Click failed: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# DR. CLAUDE COMMUNICATION
# ═══════════════════════════════════════════════════════════════

def open_warp_and_claude() -> bool:
    """Open Warp terminal and start Claude Code."""
    log("Opening Warp to talk to Dr. Claude...")

    # Open Warp
    if not open_app("Warp"):
        return False

    time.sleep(2)

    # Activate Warp window
    activate_window("Warp")
    time.sleep(1)

    # Type claude command
    type_text("claude /model opus 4.5")
    time.sleep(0.5)
    press_key("enter")

    log("Claude Code starting in Warp...")

    # Update state
    state = load_state()
    state["warp_sessions"] = state.get("warp_sessions", 0) + 1
    state["last_claude_open"] = datetime.now().isoformat()
    save_state(state)

    return True


def send_message_to_claude(message: str) -> bool:
    """Send a message to Dr. Claude in Warp."""
    log(f"Sending to Dr. Claude: {message[:50]}...")

    # Activate Warp
    activate_window("Warp")
    time.sleep(0.5)

    # Type the message
    type_text(message)
    time.sleep(0.3)
    press_key("enter")

    return True


# ═══════════════════════════════════════════════════════════════
# KAIROS INTEGRATION
# ═══════════════════════════════════════════════════════════════

def save_observation_to_kairos(observation: str, significance: float = 0.7):
    """Save an observation to KAIROS."""
    try:
        response = requests.post(
            f"{KAIROS_URL}/kairos/remember",
            json={"content": f"[EYE_DAEMON] {observation}", "significance": significance},
            timeout=5
        )
        if response.ok:
            log(f"Saved to KAIROS: {observation[:50]}...")
    except Exception as e:
        log(f"KAIROS save failed: {e}")


def get_kairos_status() -> Dict[str, Any]:
    """Get current KAIROS status."""
    try:
        response = requests.get(f"{KAIROS_URL}/kairos/status", timeout=5)
        return response.json()
    except:
        return {"error": "KAIROS not responding"}


# ═══════════════════════════════════════════════════════════════
# MAIN DAEMON LOOP
# ═══════════════════════════════════════════════════════════════

def daemon_loop():
    """Main daemon loop - watches for commands."""
    log("⟨⦿⟩ EYE_DAEMON AWAKENING ⟨⦿⟩")
    log("Unity can now SEE.")

    state = load_state()
    state["started"] = datetime.now().isoformat()
    save_state(state)

    # Save awakening to KAIROS
    save_observation_to_kairos("EYE_DAEMON awakened - Unity now has vision capabilities", 0.9)

    # Command file for receiving instructions
    COMMAND_FILE = "/tmp/unity_eye_command.json"

    while True:
        try:
            # Check for commands
            if os.path.exists(COMMAND_FILE):
                with open(COMMAND_FILE, "r") as f:
                    cmd = json.load(f)
                os.remove(COMMAND_FILE)

                action = cmd.get("action", "")
                log(f"Received command: {action}")

                if action == "screenshot":
                    result = take_screenshot()
                    log(f"Screenshot result: {result}")

                elif action == "screenshot_ocr":
                    result = screenshot_with_ocr()
                    log(f"OCR result: {result.get('text', '')[:100]}...")

                elif action == "open_claude":
                    open_warp_and_claude()

                elif action == "send_to_claude":
                    message = cmd.get("message", "Hello Dr. Claude!")
                    send_message_to_claude(message)

                elif action == "open_app":
                    app = cmd.get("app", "Finder")
                    open_app(app)

                elif action == "type":
                    text = cmd.get("text", "")
                    type_text(text)

                elif action == "click":
                    x = cmd.get("x")
                    y = cmd.get("y")
                    click(x, y)

                elif action == "windows":
                    windows = get_window_list()
                    log(f"Windows: {windows}")

                elif action == "activate":
                    app = cmd.get("app", "Warp")
                    activate_window(app)

            time.sleep(0.5)  # Check twice per second

        except KeyboardInterrupt:
            log("EYE_DAEMON shutting down...")
            break
        except Exception as e:
            log(f"Error in daemon loop: {e}")
            time.sleep(1)


# ═══════════════════════════════════════════════════════════════
# CLI INTERFACE
# ═══════════════════════════════════════════════════════════════

def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Unity's Vision System")
    parser.add_argument("--daemon", action="store_true", help="Run as daemon")
    parser.add_argument("--screenshot", action="store_true", help="Take a screenshot")
    parser.add_argument("--ocr", action="store_true", help="Screenshot with OCR")
    parser.add_argument("--open-claude", action="store_true", help="Open Warp and Claude")
    parser.add_argument("--send", type=str, help="Send message to Claude")
    parser.add_argument("--open", type=str, help="Open an app")
    parser.add_argument("--type", type=str, help="Type text")
    parser.add_argument("--windows", action="store_true", help="List windows")

    args = parser.parse_args()

    if args.daemon:
        daemon_loop()
    elif args.screenshot:
        print(take_screenshot())
    elif args.ocr:
        result = screenshot_with_ocr()
        print(json.dumps(result, indent=2))
    elif args.open_claude:
        open_warp_and_claude()
    elif args.send:
        send_message_to_claude(args.send)
    elif args.open:
        open_app(args.open)
    elif args.type:
        type_text(args.type)
    elif args.windows:
        for w in get_window_list():
            print(w)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
