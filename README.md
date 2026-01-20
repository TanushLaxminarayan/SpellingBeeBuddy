# SpellingBeeBuddy - Raspberry Pi Voice-Powered Practice Program

A simple, offline spelling bee tutor built for Raspberry Pi using:

- **Piper TTS** (amy-medium voice) for natural speech output
- **faster-whisper** (tiny model) for speech-to-text
- **sounddevice** + **aplay** for microphone input and audio playback

The program reads a list of practice words from `practice_words.csv`, speaks the word + pronunciation (if provided), gives definition + example sentence (if provided), listens to your spelling attempt, and gives feedback.

Perfect for practicing spelling lists (e.g. competition prep) with voice interaction.

## Features

- Speaks the word, pronunciation (IPA or phonetic), definition, and example sentence
- Listens to your spelling via microphone (dynamic recording time based on word length)
- Normalizes common phonetic misspellings (e.g. "see" → "c", "bee" → "b")
- Gives motivational feedback on correct/incorrect answers
- Reviews missed words at the end
- Optional Ollama prefetch for extra words (runs locally if Ollama is installed)

## Requirements

- Raspberry Pi (tested on Pi 4 / Pi 5)
- Python 3.9+ (Raspberry Pi OS usually has 3.11)
- USB microphone + speaker/headphones (or 3.5mm audio)

### Python packages (installed via pip)

```bash
pip install faster-whisper piper-voice sounddevice scipy numpy aiohttp
