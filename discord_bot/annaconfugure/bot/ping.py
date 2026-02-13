import subprocess
import time
import os
from datetime import datetime

def run_bot():
    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Running bot.py...")
        # Get the directory where bot.py is located
        bot_dir = os.path.dirname(os.path.abspath(__file__))
        bot_path = os.path.join(bot_dir, 'bot.py')
        
        # Run bot and wait for 50 seconds or until it exits
        process = subprocess.Popen(['python', bot_path])
        
        try:
            # Wait for 50 seconds
            process.wait(timeout=50)
        except subprocess.TimeoutExpired:
            # If still running after 50 seconds, terminate and restart
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Restarting bot.py (50s limit reached)...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        
        # Wait a bit before next run if it crashed early
        time.sleep(2)

if __name__ == "__main__":
    run_bot()
