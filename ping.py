import subprocess
import os
import sys
from datetime import datetime

def run_services():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Starting services...")

    try:
        # Start website
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Starting website on port 5000...")
        web_process = subprocess.Popen(
            [sys.executable, "app.py"],
            env={**os.environ, "PORT": "5000"}
        )

        # Start bot
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Starting bot.py...")
        bot_process = subprocess.Popen([sys.executable, "bot.py"])

        # Wait for both to run forever
        web_process.wait()
        bot_process.wait()

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error: {e}")

if __name__ == "__main__":
    run_services()
