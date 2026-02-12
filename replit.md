# replit.md

## Overview

This is a Discord bot project called "Anna" built with both Python (discord.py) and Node.js (Express). The project has multiple components:

1. **Discord Bot (Python)** - The main bot (`bot.py`) that responds to commands with the prefix "anna" or "!", rotates through nature-themed status messages, and includes authorization controls for trusted users.
2. **Web Server (Node.js/Express)** - A simple Express server (`index.js`) that serves a static HTML page, likely used as a keep-alive mechanism for the bot on Replit.
3. **Voice Channel Bot** (`vc.py`) - A separate bot script that joins voice channels when users join and plays a hello sound.
4. **Avatar Generator** (`s.py`) - A utility script that generates an animated GIF avatar with sparkle effects using Pillow.
5. **Bot Restarter** (`ping.py`) - A watchdog script that continuously restarts `bot.py` every 50 seconds if it crashes.
6. **Discord Rich Presence** (`bot_rich.js`) - A small Node.js script for Discord RPC status display.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Bot Architecture
- **Primary Language**: Python using `discord.py` with the `commands` extension
- **Command Prefixes**: The bot accepts both `"anna"` and `"!"` as command prefixes
- **Intents**: Uses `discord.Intents.all()` for full access to Discord events (members, messages, voice states, etc.)
- **Authorization**: Hardcoded list of trusted usernames (`AUTHORIZED_USERS`) for admin-level commands
- **Status Rotation**: A `tasks.loop` that cycles through nature/Pokemon-themed status messages every 2 seconds
- **Token Management**: Uses `python-dotenv` to load `DISCORD_TOKEN` from a `.env` file. The token should be stored as a Replit Secret or in `.env`.

### Web Server Architecture
- **Framework**: Express.js (v4) serving static files from a `public/` directory
- **Purpose**: Acts as a keep-alive web server so the Replit stays awake. Serves `index.html` which shows a "Pinging Anna" status page.
- **Port**: Runs on port 3000 internally, mapped to port 80 externally by Replit.

### Process Management
- `ping.py` acts as a simple process supervisor, restarting `bot.py` in a loop with 50-second intervals between restarts.
- The Express server (`index.js`) runs independently to keep the Replit alive.

### Key Design Decisions
- **Dual runtime (Python + Node.js)**: The bot logic runs in Python while the keep-alive server runs in Node.js. This means both runtimes need to be available.
- **Multiple bot scripts**: There are several bot files (`bot.py`, `Test.py`, `vc.py`) that appear to be different iterations or features. `bot.py` is the main one run by `ping.py`.
- **No database**: Currently no persistent storage — all configuration is hardcoded or in environment variables.
- **No formal deployment pipeline**: The bot runs directly via `ping.py` calling `bot.py` in a subprocess loop.

### Important Files
| File | Purpose |
|------|---------|
| `bot.py` | Main Discord bot with commands and status rotation |
| `ping.py` | Watchdog that restarts bot.py continuously |
| `index.js` | Express web server for keep-alive |
| `index.html` | Static status page |
| `vc.py` | Voice channel joining bot (separate feature) |
| `s.py` | Avatar GIF generator utility |
| `Test.py` | Test bot for setting avatar |
| `bot_rich.js` | Discord Rich Presence client |
| `.env` | Environment variables (DISCORD_TOKEN) |

## External Dependencies

### Python Dependencies
- **discord.py** (`discord`, `discord.ext.commands`, `discord.app_commands`) - Discord bot framework
- **python-dotenv** - Loading environment variables from `.env` files
- **Pillow** (`PIL`) - Image processing for avatar generation (used in `s.py`)
- **requests** - HTTP requests for downloading avatar images

### Node.js Dependencies (from package.json)
- **express** (v4.19.2) - Web server framework for keep-alive endpoint
- **discord-rpc** (v4.0.1) - Discord Rich Presence client
- **nodemon** (v3.0.3, dev) - Auto-restart for Node.js development

### Environment Variables
| Variable | Required | Purpose |
|----------|----------|---------|
| `DISCORD_TOKEN` | Yes | Discord bot authentication token. Must be set as a Replit Secret or in `.env` |

### External Services
- **Discord API** - Primary integration for the bot functionality
- **Discord CDN** - Used for downloading avatar images in the avatar generator script