# audio/wakeword.py
import pvporcupine
import pyaudio
import struct

porcupine = pvporcupine.create(keywords=["hey SpellingBee Buddy"])
pa = pyaudio.PyAudio()

stream = pa.open(
    rate=porcupine.sample_rate,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    frames_per_buffer=porcupine.frame_length
)

def listen():
    pcm = stream.read(porcupine.frame_length, exception_on_overflow=False)
    pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
    return porcupine.process(pcm) >= 0
