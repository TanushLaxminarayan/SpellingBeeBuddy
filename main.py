# main.py
from core.words import load_words
from core.game import run_game
from audio.tts import speak

def main():
    words = load_words()
    score, missed = run_game(words)

    speak(f"You scored {score} points!")
    if missed:
        speak("Let's review missed words.")
        for w in missed:
            speak(w["word"])
    speak("See you next time!")

if __name__ == "__main__":
    main()
