# ARIA_ai_assistant

**ARIA** is a voice-activated personal AI assistant developed in Python. It uses Vosk for offline speech recognition and Google's Gemini API for generating intelligent responses. Vox listens for the wake word **"Vox"**, responds with **"Yes, sire!"**, then records your next spoken input and sends it to Gemini for a response.

## Features

- Voice-activated trigger using the keyword "Aria"
- Manual recording controls using keyboard keys
- Integration with Google's Gemini language model
- Built-in personality: Vox responds as a polite, witty personal assistant
- English language support (tagalog support will be added in the future)

## Requirements

Install all required Python libraries with the following command:

```bash
pip install vosk sounddevice keyboard requests

pip install PyQt5
