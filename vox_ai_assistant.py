import os
import queue
import sounddevice as sd
import json
import threading
import keyboard
import requests
from vosk import Model, KaldiRecognizer

#CONFIGURATION
LANGUAGE = "english"
MODEL_PATHS = {
    "english": "models/vosk-model-small-en-us-0.15",
}

GEMINI_API_KEY = "AIzaSyBXMqCFlBgnm9cFwlWLXTNVC-vJKKlz2MA"  
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

samplerate = 16000
device = None

#MODEL
if LANGUAGE not in MODEL_PATHS:
    raise ValueError("Unsupported language")

if not os.path.exists(MODEL_PATHS[LANGUAGE]):
    raise FileNotFoundError(f"Model not found at {MODEL_PATHS[LANGUAGE]}")

model = Model(MODEL_PATHS[LANGUAGE])
q = queue.Queue()
recording = False
recognizer = KaldiRecognizer(model, samplerate)
result_text = []
vox_activated = False

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Audio error: {status}")
    q.put(bytes(indata))

#GEMINI
def send_to_gemini(user_input):
    headers = {"Content-Type": "application/json"}

    system_message = (
        "You are Vox, a smart, witty, and polite personal assistant AI. "
        "You are helpful, concise, and always respond as if you're speaking to your user personally."
    )

    data = {
        "contents": [
            {
                "parts": [
                    {"text": system_message},
                    {"text": user_input}
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_URL, headers=headers, json=data)
        if response.status_code == 200:
            content = response.json()
            return content['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Exception while calling Gemini: {e}"

#AUDIO RECORDING
def recorder():
    global recording, result_text, vox_activated
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16',
                           channels=1, callback=audio_callback, device=device):
        print("Vox is ready. Say 'Vox' to begin. Press 's' to manually record. Press 'q' to stop.")
        while True:
            if recording:
                try:
                    data = q.get()
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        if result.get("text"):
                            print("Input: ", result["text"])
                            result_text.append(result["text"])
                except Exception as e:
                    print(f"Recording error: {e}")
            else:
                '''
                keyboard.wait('s')
                if not recording:
                    print("\nManual recording started. Press 'q' to stop.")
                    result_text = []
                    recording = True
                '''
                try:
                    data = q.get()
                    if recognizer.AcceptWaveform(data):
                        result = json.loads(recognizer.Result())
                        spoken = result.get("text", "").lower().strip()
                        if spoken == "vox":
                            print("Vox: Yes, sire!")
                            vox_activated = True
                            print("Vox:I'm listening just press 'q' when you're done.")
                            result_text = []
                            recording = True
                except Exception as e:
                    print(f"Passive listen error: {e}")

#KEYBOARD COMMAND
def listen_for_keys():
    global recording, result_text, vox_activated
    while True:
        keyboard.wait('q')
        if recording:
            print("Recording stopped.")
            recording = False

            final_result = json.loads(recognizer.FinalResult())
            if final_result.get("text"):
                result_text.append(final_result["text"])

            full_text = " ".join(result_text)
            print("\nFull transcription:")
            print(full_text)

            '''
            if vox_activated:
                vox_activated = False
                print("\nSending prompt to Gemini...")
                response = send_to_gemini(full_text)
                print("\nVox says:")
                print(response)
            else:
                print("\nIgnored — no wake word used.")
            '''
                
            print("\nSending prompt to Gemini...")
            response = send_to_gemini(full_text)
            print("\nVox:")
            print(response)

            print("\nPress 's' or say 'Vox' again to continue.\n")

        keyboard.wait('s')
        if not recording:
            print("\nManual recording started. Press 'q' to stop.")
            result_text = []
            recording = True

if __name__ == "__main__":
    try:
        threading.Thread(target=recorder, daemon=True).start()
        listen_for_keys()
    except KeyboardInterrupt:
        print("\nHappy to assist you sire.")
