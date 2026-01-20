# wake_listener.py
import time
import subprocess
from audio.wakeword import listen

print("Spelling Buddy sleeping...")

while True:
    if listen():
        subprocess.call(["python3", "main.py"])
        time.sleep(2)
