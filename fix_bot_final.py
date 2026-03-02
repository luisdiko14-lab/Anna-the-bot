import re

def fix():
    with open("bot.py", "r") as f:
        lines = f.readlines()
    
    new_lines = []
    
    # Heuristic for module-level patterns that MUST be at zero indentation
    zero_indent_patterns = [
        r'^import\s+', r'^from\s+', r'^@bot\.', r'^@tasks\.', r'^@app_commands\.', 
        r'^@change_status\.', r'^async\s+def\s+', r'^def\s+', r'^class\s+', 
        r'^TOKEN\s*=', r'^AUTHORIZED_USERS\s*=', r'^PREFIX\s*=', r'^intents\s*=', 
        r'^bot\s*=', r'^nature_scenes\s*=', r'^load_dotenv\(', r'^if\s+not\s+TOKEN:',
        r'^#\s+===', r'^#\s+---', r'^@change_status', r'^@app_commands', r'^nature_scenes\s*='
    ]
    
    # Keywords that start a block
    block_starters = ('if ', 'def ', 'async def ', 'class ', 'elif ', 'else:', 'try:', 'except ', 'finally:', 'with ', 'async with ', 'for ', 'while ')

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip()
        if not stripped:
            new_lines.append("\n")
            i += 1
            continue
            
        should_be_zero = any(re.match(p, stripped) for p in zero_indent_patterns)
        
        if should_be_zero:
            new_lines.append(stripped)
            # If it is a block-starter, indent EVERYTHING until the next module-level line
            if stripped.endswith(":") or stripped.startswith(block_starters):
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    next_stripped = next_line.lstrip()
                    if not next_stripped:
                        new_lines.append("\n")
                        i += 1
                        continue
                    if any(re.match(p, next_stripped) for p in zero_indent_patterns):
                        i -= 1
                        break
                    
                    # Force 4-space indentation for the block
                    if next_line.startswith("            "):
                        new_lines.append("        " + next_stripped)
                    else:
                        new_lines.append("    " + next_stripped)
                    i += 1
        else:
            if line.startswith("        "):
                new_lines.append("    " + stripped)
            else:
                new_lines.append(line)
        i += 1
            
    with open("bot.py", "w") as f:
        f.writelines(new_lines)

fix()

# Post-processing for specific syntax errors
with open("bot.py", "r") as f:
    content = f.read()

# Ensure nature_scenes is correctly formatted
content = re.sub(r"nature_scenes = \[.*?\]", """nature_scenes = [
    "Pokemon! 🌲",
    "MEW! 🌅",
    "Flowing Rivers 🌊",
    "Pikachu 🏔️",
    "Starry Nights 🌌",
    "Blooming Pokemons 🌸",
    "Falling Rain 🌧️",
    "Mew is cool! i like it",
    "Just Got verified! ✅"
]""", content, flags=re.DOTALL)

# Fix on_ready return and status start
content = content.replace('if hasattr(bot, "ready_ran") and bot.ready_ran:', 'if hasattr(bot, "ready_ran") and bot.ready_ran:\n        return')
content = content.replace('if not change_status.is_running():', 'if not change_status.is_running():\n        change_status.start()')

# Fix empty blocks
content = re.sub(r"(try:|except.*?|else:|finally:)\s*\n\s*(?=@|async def|def|class|if|TOKEN|AUTHORIZED_USERS|PREFIX|intents|bot|load_dotenv|#|nature_scenes)", r"\1\n        pass\n", content)

with open("bot.py", "w") as f:
    f.write(content)
