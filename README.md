# SpellingBeeBuddy

**Offline, voice-powered spelling bee practice tutor** for Raspberry Pi.

SpellingBeeBuddy reads words from a CSV (or TXT) file, speaks each word clearly (with optional pronunciation, definition, and example sentence), listens to your spoken spelling attempt via microphone, evaluates it, gives instant feedback, and reviews any missed words at the end.

Completely offline after initial model downloads — ideal for spelling bee competition prep or general practice.

## Features

- Natural TTS using **Piper** (amy-medium voice by default)
- Accurate speech-to-text with **faster-whisper** (tiny.en model recommended)
- Speaks: word + pronunciation (if provided) + definition + example sentence
- Dynamic microphone recording duration based on word length
- Smart normalization of common phonetic misspellings (e.g. "see" → "c", "bee" → "b")
- Motivational audio & spoken feedback for correct/incorrect answers
- Automatic end-of-session review for missed words
- Optional local **Ollama** integration to fetch missing word info (definitions/pronunciations)

## Requirements

- **Hardware**
  - Raspberry Pi 4 or 5 (tested on these)
  - USB microphone (strongly recommended) or working mic input
  - Speakers or headphones (3.5 mm jack, USB, or HDMI audio)

- **Software**
  - Raspberry Pi OS (64-bit preferred) with Python 3.9+
  - Working audio input & output (test with `arecord` / `aplay`)

## Installation

1. **Update your system & install basics**

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install python3-pip python3-venv git -y

Clone the repositoryBashgit clone https://github.com/TanushLaxminarayan/SpellingBeeBuddy.git
cd SpellingBeeBuddy
(Recommended) Create and activate a virtual environmentBashpython3 -m venv venv
source venv/bin/activate
Install Python dependenciesBashpip install --upgrade pip
pip install faster-whisper piper-voice sounddevice scipy numpy aiohttpOn first run, faster-whisper and piper-voice will automatically download their models (~150–400 MB total). This requires internet only once.
Prepare your word listEdit (or create) practice_words.csv in the project folder.Simple format (minimum):textword
elephant
xylophoneAdvanced format (recommended for best experience):textword,pronunciation,definition,example
elephant,"EL-uh-fuhnt","a very large mammal with a long trunk and large ears","The elephant used its trunk to spray water."
xylophone,"ZY-luh-fone","a musical instrument with wooden bars struck by mallets","She played a tune on the xylophone."(Alternatively, use practice_words.txt — one word per line. The script defaults to CSV but you can modify it to read TXT if preferred.)

Running the Program
With the virtual environment activated (recommended):
Bashpython SpellingBee.py
Or directly:
Bashpython3 SpellingBee.py
What happens:

Loads words from practice_words.csv (or .txt)
Greets you and starts the session
For each word: speaks it (+ extras if available)
Listens for your spoken spelling
Gives immediate feedback
Reviews missed words at the end

Press Ctrl+C to exit anytime.
Optional Enhancements

Change voice or model
Edit SpellingBee.py — search for piper-voice name or faster-whisper model size (e.g. tiny.en, base.en).
Ollama support
If you run Ollama locally (ollama serve), the script can query it to fill in missing pronunciations/definitions.

Troubleshooting

No sound output?
Test speakers: aplay /usr/share/sounds/alsa/Front_Center.wav
Microphone issues?
Record & playback test:Basharecord -d 5 test.wav
aplay test.wav
Module not found?
Ensure you're inside the venv (source venv/bin/activate) and re-run pip install.
Model download fails?
Check internet; delete ~/.cache/faster-whisper or ~/.local/share/piper folders and retry.

Contributing
Pull requests welcome! Especially:

Improved phonetic correction rules
Support for more voices/models
Better CSV/TXT parsing options
Audio feedback variety

Happy spelling! 
Made with ❤️ by Tanush Laxminarayan
Richmond, Virginia