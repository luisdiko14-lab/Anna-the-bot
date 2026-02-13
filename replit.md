# replit.md

## Overview

This is a multi-component Discord bot project called "Anna" that combines a Python-based Discord bot, a Node.js/Express web server for keeping the bot alive, and several utility scripts. The project includes:

- A Discord bot (Python) with slash commands, rotating status messages, and avatar management
- A simple Express web server that serves a static HTML page (used as a keep-alive ping endpoint)
- A Discord Rich Presence client (Node.js)
- A utility script to generate an animated GIF avatar with sparkle effects
- A process runner (`ping.py`) that restarts the bot periodically

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Discord Bot (Python - Primary Application)
- **Framework**: discord.py with `commands.Bot` using the `commands` and `tasks` extensions
- **Entry Point**: `bot.py` is the main bot file; `ping.py` acts as a supervisor that restarts `bot.py` every 50 seconds if it crashes
- **Command Prefix**: Dual prefix — `"anna"` and `"!"`
- **Intents**: Uses `discord.Intents.all()` for full gateway intent access
- **Auth Model**: Token loaded from `.env` file via `python-dotenv`; certain commands restricted to a hardcoded list of authorized Discord usernames
- **Status Rotation**: A `tasks.loop` cycles through nature/Pokémon-themed status messages every 67 seconds

### Web Server (Node.js - Keep-Alive)
- **Framework**: Express.js v4
- **Purpose**: Serves a static HTML page on port 3000 to keep the Replit project alive via external pinging services
- **Entry Point**: `index.js`
- **Static Files**: Served from a `public/` directory; `index.html` is the landing page

### Avatar Generator (`s.py`)
- **Purpose**: Downloads the bot's Discord avatar, overlays random sparkle/emoji decorations, and saves as an animated GIF
- **Libraries**: Pillow (PIL), requests
- **Output**: `avatar_with_drawn_emojis.gif` used by `Test.py` and `bot.py` to set the bot's profile picture

### Discord Rich Presence (`bot_rich.js`)
- **Library**: `discord-rpc`
- **Purpose**: Sets a custom Rich Presence status for a Discord application (separate from the bot itself)

### Process Architecture
- `ping.py` runs in a loop, launching `bot.py` via subprocess and restarting it after 50 seconds — a simple crash recovery mechanism
- The Express server runs independently to provide an HTTP endpoint for uptime monitoring

### Key Files
| File | Purpose |
|------|---------|
| `bot.py` | Main Discord bot with commands, status loop, event handling |
| `ping.py` | Supervisor script that restarts bot.py periodically |
| `Test.py` | Standalone script for setting bot avatar |
| `s.py` | Avatar GIF generator with sparkle effects |
| `index.js` | Express web server for keep-alive |
| `index.html` | Static landing page |
| `bot_rich.js` | Discord Rich Presence client |
| `main.py` | Default Replit entry point (placeholder) |

## External Dependencies

### Python Packages
- **discord.py** (`discord`, `discord.ext`) — Discord bot framework
- **python-dotenv** — Loads environment variables from `.env`
- **Pillow** (PIL) — Image processing for avatar generation
- **requests** — HTTP client for downloading avatar images

### Node.js Packages
- **express** (v4.19.2) — Web server framework
- **discord-rpc** (v4.0.1) — Discord Rich Presence integration
- **nodemon** (v3.0.3, dev) — Auto-restart during development

### Environment Variables
| Variable | Description |
|----------|-------------|
| `DISCORD_TOKEN` | Discord bot authentication token (required, stored in `.env`) |

### External Services
- **Discord API** — Bot operations, avatar management, Rich Presence
- **Discord CDN** — Avatar image downloads for GIF generation
- External uptime monitoring services are expected to ping the Express server to keep the Replit alive