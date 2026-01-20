# audio/stt.py
from faster_whisper import WhisperModel

print("Loading STT model...")
_MODEL = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)

def listen_for_text(timeout=4):
    """
    Listens for speech and returns lowercase text.
    """
    segments, _ = _MODEL.transcribe(
        "audio.wav",
        beam_size=1,
        vad_filter=True
    )

    text = " ".join(s.text for s in segments).strip().lower()
    return text

