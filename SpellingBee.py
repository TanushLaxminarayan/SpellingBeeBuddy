import asyncio
import aiohttp
import random
import os
import time
import numpy as np
import subprocess
import json
import csv
import sys 


# Force UTF-8 output everywhere (fixes latin-1 crash with IPA)
sys.stdout.reconfigure(encoding='utf-8')

from faster_whisper import WhisperModel
from piper.voice import PiperVoice


VOICE_MODEL_PATH = os.path.expanduser("~/.piper/en_US-amy-medium.onnx")

if not os.path.exists(VOICE_MODEL_PATH):
    print("Downloading Piper voice model...")
    os.makedirs(os.path.dirname(VOICE_MODEL_PATH), exist_ok=True)
    import urllib.request
    url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx?download=true"
    urllib.request.urlretrieve(url, VOICE_MODEL_PATH)
    print("Voice model downloaded.")

config_path = VOICE_MODEL_PATH + ".json"
if not os.path.exists(config_path):
    try:
        config_url = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json?download=true"
        urllib.request.urlretrieve(config_url, config_path)
    except:
        pass

print("Loading Piper voice model...")
piper = PiperVoice.load(VOICE_MODEL_PATH, config_path=config_path if os.path.exists(config_path) else None)
print("[OK] Piper voice loaded")

def speak(text):
    print("[SPEAK] " + text)
    try:
        raw_audio = b"".join(piper.synthesize_stream_raw(text))
        if len(raw_audio) == 0:
            print("[ERROR] No audio generated!")
            return

        rate = 22050

        subprocess.run([
            'aplay',
            '-r', str(rate),
            '-f', 'S16_LE',
            '-c', '1',
            '-t', 'raw',
            '-q'
        ], input=raw_audio, check=True)
        print("[PLAYBACK OK]")
    except subprocess.CalledProcessError as e:
        print(f"[APLAY ERROR] return code {e.returncode}")
    except Exception as e:
        print(f"[SPEAK ERROR] {e}")

def spell_word(word):
    letters = " ".join(list(word.upper()))
    spelled = f"The letters are: {letters}."
    print("[SPELLING OUT] " + spelled)
    speak(spelled)

def speak_pronunciation(pron):
    if not pron:
        return
    spoken = f"Pronounced {pron}."
    print("[PRONUNCIATION] " + spoken)
    speak(spoken)
    speak(f"Again, slowly: {pron}.")

print("=== Spelling Bee Tutor Starting ===")
print("Loading components...")

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "phi3:mini"
SAMPLE_RATE = 48000
INITIAL_PREFETCH = 3
CONCURRENCY = 2
ROUNDS = 12
MIC_DEVICE = 0

COMPETITION_WORDS = []
try:
    with open("practice_words.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            word = row.get("word", "").strip().lower()
            if word:
                entry = {
                    "word": word,
                    "pronunciation": row.get("pronunciation", "").strip(),
                    "difficulty": row.get("difficulty", "medium").strip().lower(),
                    "definition": row.get("definition", "").strip(),
                    "sentence": row.get("sentence", "").strip()
                }
                if not entry["difficulty"]:
                    length = len(word)
                    entry["difficulty"] = "easy" if length <= 6 else "medium" if length <= 9 else "hard"
                COMPETITION_WORDS.append(entry)
    print(f"[OK] Loaded {len(COMPETITION_WORDS)} words from practice_words.csv")
except FileNotFoundError:
    print("[ERROR] practice_words.csv not found! Using fallback word.")
    COMPETITION_WORDS = [{"word": "example", "pronunciation": "ig-ZAM-puhl", "difficulty": "easy", "definition": "a sample word", "sentence": "This is an example."}]
except Exception as e:
    print(f"[ERROR] Failed to read CSV: {e}")
    COMPETITION_WORDS = []

random.shuffle(COMPETITION_WORDS)
WORD_CACHE = COMPETITION_WORDS.copy()
USED_WORDS = set()
MISSED_WORDS = []
STREAK = 0

def get_recording_duration(word):
    length = len(word)
    base_time = 4 if length <= 6 else 5 if length <= 9 else 6 if length <= 12 else 7
    total = base_time + 5
    if '-' in word or sum(1 for c in word.lower() if c in 'aeiouy') >= 5:
        total += 1
    print(f"[DEBUG] Recording {total} seconds for '{word}'")
    return total

def motivational_feedback(correct):
    if correct:
        phrases = ["Amazing! You're a spelling superstar!", "Yes! You nailed it! Keep shining!", "Fantastic! You're getting better every time!", "Perfect! High five!"]
    else:
        phrases = ["Great try! Practice makes perfect!", "Almost there! You're so close!", "Don't worry, you'll get it next time!", "Good effort! Let's keep going!"]
    msg = random.choice(phrases)
    speak(msg)

print("Loading Whisper tiny model...")
whisper = WhisperModel("tiny", device="cpu", compute_type="int8")
print("[OK] Whisper model loaded")

import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile

def record_audio(word):
    duration = get_recording_duration(word)
    print(f"[PROMPT] Spell the word now. Recording for {duration} seconds.")
    speak("Spell the word now.")
    print(f"[RECORDING] {duration} seconds...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.int16, device=MIC_DEVICE)
    sd.wait()
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav.write(temp_file.name, SAMPLE_RATE, audio)
    print("[RECORDED]")
    return temp_file.name

def transcribe(audio_file):
    print("[TRANSCRIBING]...")
    segments, _ = whisper.transcribe(audio_file, beam_size=5)
    text = " ".join(segment.text for segment in segments).strip().lower()
    print(f"[RAW] '{text}'")
    return text

def normalize_spelling(text):
    replacements = {
        "see": "c", "sea": "c", "ay": "a", "bee": "b", "cee": "c",
        "dee": "d", "ee": "e", "ef": "f", "gee": "g", "aitch": "h",
        "eye": "i", "jay": "j", "kay": "k", "el": "l", "em": "m",
        "en": "n", "oh": "o", "pee": "p", "queue": "q", "ar": "r",
        "ess": "s", "tee": "t", "you": "u", "vee": "v", "double you": "w",
        "ex": "x", "why": "y", "zee": "z", "zed": "z"
    }
    for word, letter in replacements.items():
        text = text.replace(word, letter)
    text = text.replace("-", "").replace(" ", "").replace(".", "").replace(",", "")
    return text

async def fetch_word(session, semaphore):
    prompt = "Give ONE unique elementary spelling bee word as JSON only: {\"word\":\"example\",\"difficulty\":\"easy\",\"definition\":\"meaning\",\"sentence\":\"Example use.\"}"
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    async with semaphore:
        try:
            async with session.post(OLLAMA_URL, json=payload, timeout=120) as resp:
                data = await resp.json()
                response = data.get("response", "").strip()
                response = response.strip('```json').strip('```').strip()
                info = json.loads(response)
                word = info["word"].lower()
                if word not in USED_WORDS:
                    USED_WORDS.add(word)
                    return {"word": word, "definition": info.get("definition",""), "sentence": info.get("sentence",""), "difficulty": info.get("difficulty","easy")}
        except Exception as e:
            print(f"[INFO] LLM fetch failed: {e}")
        return None

async def initial_prefetch():
    print("[INFO] Prefetching words from Ollama...")
    words = []
    semaphore = asyncio.Semaphore(CONCURRENCY)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_word(session, semaphore) for _ in range(INITIAL_PREFETCH)]
        results = await asyncio.gather(*tasks)
        for w in results:
            if w:
                words.append(w)
    WORD_CACHE.extend(words)
    print(f"[OK] Prefetched {len(words)} new words")
    random.shuffle(WORD_CACHE)

def run_round(word_info):
    global STREAK, MISSED_WORDS
    word = word_info["word"]
    pron = word_info.get("pronunciation", "")
    definition = word_info.get("definition", "")
    sentence = word_info.get("sentence", "")
    
    print(f"\n--- Round: {word.upper()} ({word_info['difficulty']}) ---")
    speak(word_info["difficulty"].capitalize() + " level word.")
    speak("The word is " + word + ".")
    
    if pron:
        speak_pronunciation(pron)
    
    if definition:
        speak("Definition: " + definition)
    if sentence:
        speak("Example sentence: " + sentence)
    
    audio_file = record_audio(word)
    spoken = normalize_spelling(transcribe(audio_file))
    os.remove(audio_file)
    
    if spoken == word:
        print("[CORRECT]")
        STREAK += 1
        motivational_feedback(True)
        if STREAK % 3 == 0:
            speak(f"Level up! {STREAK} in a row! You're unstoppable!")
        return 1
    else:
        print(f"[INCORRECT] (heard: '{spoken}')")
        STREAK = 0
        motivational_feedback(False)
        speak("The correct spelling is:")
        spell_word(word)
        MISSED_WORDS.append(word_info)
        return 0

def review_missed():
    if MISSED_WORDS:
        speak("Let's quickly review the words you missed. You've got this!")
        for w in MISSED_WORDS:
            speak("Word: " + w["word"] + ".")
            pron = w.get("pronunciation", "")
            if pron:
                speak_pronunciation(pron)
            if w.get("definition"):
                speak("Definition: " + w["definition"])
            speak("Repeat after me:")
            spell_word(w["word"])
            speak("Great job practicing!")
    else:
        speak("Wow! You got every word perfect! You're a spelling champion!")

async def main():
    await initial_prefetch()
    print("[INFO] Starting the spelling bee game!")
    speak("Hey superstar! Welcome to the spelling bee! Let's have fun and get better together!")
    
    score = 0
    for i in range(ROUNDS):
        difficulty = "easy" if i < 4 else "medium" if i < 8 else "hard"
        word_info = next((w for w in WORD_CACHE if w["difficulty"] == difficulty), None)
        if word_info is None:
            if WORD_CACHE:
                word_info = WORD_CACHE.pop(0)
            else:
                word_info = random.choice(COMPETITION_WORDS)
        if word_info in WORD_CACHE:
            WORD_CACHE.remove(word_info)
        USED_WORDS.add(word_info["word"])
        score += run_round(word_info)
    
    speak(f"Game over! You scored {score} out of {ROUNDS}! Amazing effort!")
    print(f"[RESULT] Final score: {score}/{ROUNDS}")
    review_missed()
    speak("You're getting smarter every day. Keep practicing! See you next time!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print("[CRASH] " + str(e))
        import traceback
        traceback.print_exc()
