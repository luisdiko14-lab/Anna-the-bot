import subprocess
import time
import os
import sys
import requests
from datetime import datetime

PING_URL = "http://127.0.0.1:5000"  # Change to your deployed URL if needed

def run_services():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Starting services...")

    # Start website
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🌐 Starting website on port 5000...")
    web_process = subprocess.Popen(
        [sys.executable, "app.py"],
        env={**os.environ, "PORT": "5000"}
    )

    # Start bot
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🤖 Starting bot.py...")
    bot_process = subprocess.Popen([sys.executable, "bot.py"])

    try:
        while True:
            try:
                response = requests.get(PING_URL)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔔 Pinged site | Status: {response.status_code}")
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Ping failed: {e}")

            time.sleep(15)  # Ping every 15 seconds

    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")

    finally:
        for process in [web_process, bot_process]:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

if __name__ == "__main__":
    run_services()
