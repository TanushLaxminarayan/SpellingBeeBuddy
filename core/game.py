# core/game.py
from audio.tts import speak
from audio.stt import transcribe, detect_command

def speak_pronunciation(pron):
    if pron:
        speak(f"Pronounced {pron}.")
        speak(f"Again, slowly: {pron}.")

def run_game(words, rounds=12):
    missed = []
    score = 0

    speak("Welcome to Spelling Bee Buddy!")

    for i, info in enumerate(words[:rounds]):
        word = info["word"]
        difficulty = info.get("difficulty", "medium")
        definition = info.get("definition", "")
        sentence = info.get("sentence", "")
        pronunciation = info.get("pronunciation", "")

        speak(f"{difficulty.capitalize()} level word.")
        speak(f"The word is {word}.")

        # ✅ Pronunciation
        speak_pronunciation(pronunciation)

        # ✅ Definition
        if definition:
            speak("Definition:")
            speak(definition)

        # ✅ Example sentence
        if sentence:
            speak("Example sentence:")
            speak(sentence)

        while True:
            speak("Spell the word.")
            response = transcribe(5)
            cmd = detect_command(response)

            # 🎤 Voice commands
            if cmd == "repeat":
                speak("Repeating the word.")
                speak(f"The word is {word}.")
                speak_pronunciation(pronunciation)
                continue

            if cmd == "skip":
                speak("Skipping this word.")
                missed.append(info)
                break

            if cmd == "quit":
                speak("Ending practice. Great job today!")
                return score, missed

            # ✅ Spelling check
            if response == word:
                speak("Correct! Excellent spelling!")
                score += 1
                break
            else:
                speak("That is not correct.")
                speak("Try again, or say repeat or skip.")

    return score, missed
