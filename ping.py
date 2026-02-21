import subprocess
import time
import os
import sys
from datetime import datetime

def run_bot():
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Starting bot.py...")
        try:
            # Run bot.py and wait for it to finish
            process = subprocess.Popen([sys.executable, "bot.py"])
            
            # Wait for the process to exit or for 50 seconds
            # This logic mimics the original request to restart every 50s
            # but also handles crashes gracefully.
            try:
                process.wait(timeout=50)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ bot.py exited. Restarting...")
            except subprocess.TimeoutExpired:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 50 seconds elapsed. Restarting bot.py for maintenance...")
                process.terminate()
                process.wait()
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Error running bot.py: {e}")
        
        time.sleep(2) # Small delay before restart

if __name__ == "__main__":
    run_bot()
