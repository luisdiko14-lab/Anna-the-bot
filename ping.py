import subprocess
import os
import sys
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def run_services():
    log("🚀 Starting services...")

    try:
        # Start bot first
        log("🤖 Starting bot.py...")
        bot_process = subprocess.Popen([sys.executable, "bot.py"])

        # Then start website
        log("🌐 Starting website on port 5000...")
        web_process = subprocess.Popen(
            [sys.executable, "app.py"],
            env={**os.environ, "PORT": "5000"}
        )

        log("✅ Both services are running!")
        
        # Wait for both to finish (usually run forever)
        bot_process.wait()
        web_process.wait()

    except Exception as e:
        log(f"❌ Error: {e}")

if __name__ == "__main__":
    run_services()
