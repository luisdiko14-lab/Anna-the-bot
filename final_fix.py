import sys
import re

def fix():
    with open("bot.py", "r") as f:
        lines = f.readlines()
    
    new_lines = []
    # Identify lines that must be at 0 indent
    zero_patterns = [
        r'^import\s', r'^from\s', r'^@bot\.', r'^@tasks\.', r'^@app_commands\.', 
        r'^async\s+def\s', r'^def\s', r'^class\s', r'^TOKEN\s*=', r'^AUTHORIZED_USERS\s*=',
        r'^PREFIX\s*=', r'^intents\s*=', r'^bot\s*=', r'^nature_scenes\s*=', 
        r'^load_dotenv\(', r'^if\s+not\s+TOKEN:', r'^#\s+===', r'^#\s+---', r'^nature_scenes\s*='
    ]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        
        is_zero = False
        for p in zero_patterns:
            if re.match(p, stripped):
                is_zero = True
                break
        
        if is_zero:
            new_lines.append(stripped)
            if stripped.startswith("if not TOKEN:"):
                i += 1
                new_lines.append("    print(\"Token Error\")\n")
                new_lines.append("    exit()\n")
                # skip next lines if they were the old print/exit
                while i < len(lines) and ("Token not found" in lines[i] or "exit()" in lines[i]):
                    i += 1
                continue
        elif line.startswith("        "):
            new_lines.append("    " + stripped)
        else:
            new_lines.append(line)
        i += 1
        
    with open("bot.py", "w") as f:
        f.writelines(new_lines)

fix()
