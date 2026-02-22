import subprocess
import time
import os
import sys
from datetime import datetime

def run_services():
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Starting services...")

        try:
            # Start website (change app.py if your file is different)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Starting website on port 5000...")
            web_process = subprocess.Popen(
                [sys.executable, "app.py"],
                env={**os.environ, "PORT": "5000"}
            )

            # Start bot
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Starting bot.py...")
            bot_process = subprocess.Popen([sys.executable, "bot.py"])

            try:
                # Wait 50 seconds
                time.sleep(100)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Restarting services for maintenance...")

            finally:
                # Terminate both processes safely
                for process in [web_process, bot_process]:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()

        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {e}")

        time.sleep(2)

if __name__ == "__main__":
    run_services()
