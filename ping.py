import subprocess
import time
from datetime import datetime

while True: ### I changed it.
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Running bot.py...")

    subprocess.run(["python", "bot.py"])

    time.sleep(50)


# ==========================
# STATUS 