# audio/tts.py
import os
import subprocess
from piper.voice import PiperVoice
import urllib.request

VOICE_MODEL_PATH = os.path.expanduser("~/.piper/en_US-amy-medium.onnx")
CONFIG_PATH = VOICE_MODEL_PATH + ".json"

if not os.path.exists(VOICE_MODEL_PATH):
    os.makedirs(os.path.dirname(VOICE_MODEL_PATH), exist_ok=True)
    urllib.request.urlretrieve(
        "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx?download=true",
        VOICE_MODEL_PATH
    )

if not os.path.exists(CONFIG_PATH):
    try:
        urllib.request.urlretrieve(
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json?download=true",
            CONFIG_PATH
        )
    except:
        CONFIG_PATH = None

piper = PiperVoice.load(VOICE_MODEL_PATH, config_path=CONFIG_PATH)

def speak(text):
    print("[SPEAK]", text)
    raw_audio = b"".join(piper.synthesize_stream_raw(text))
    subprocess.run(
        ["aplay", "-r", "22050", "-f", "S16_LE", "-c", "1", "-t", "raw", "-q"],
        input=raw_audio,
        check=True
    )
