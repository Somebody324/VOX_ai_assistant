# VOX_ai_assistant

**Vox** is a voice-activated personal AI assistant developed in Python. It uses Vosk for offline speech recognition and Google's Gemini API for generating intelligent responses. Vox listens for the wake word **"Vox"**, responds with **"Yes, sire!"**, then records your next spoken input and sends it to Gemini for a response.

## Features

- Voice-activated trigger using the keyword "Vox"
- Manual recording controls using keyboard keys
- Integration with Google's Gemini language model
- Built-in personality: Vox responds as a polite, witty personal assistant
- English language support (with optional Tagalog support)

## Requirements

Install all required Python libraries with the following command:

```bash
pip install vosk sounddevice keyboard requests
