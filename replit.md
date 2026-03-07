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
- **Entry Point**: `bot.py` with 76+ synced slash commands and moderation tools
- **Command Prefix**: Dual prefix — `"anna"` and `"!"`
- **Intents**: Uses `discord.Intents.all()` for full gateway intent access
- **Auth Model**: Token loaded from `.env` file via `python-dotenv`; certain commands restricted to authorized usernames
- **Status Rotation**: A `tasks.loop` cycles through nature/Pokémon-themed status messages
- **Message Handler**: `on_message` event listener for prefix command processing

### Web Server (Node.js - Express)
- **Framework**: Express.js v4 with Passport.js for Discord OAuth
- **Purpose**: Serves premium dashboard with Discord authentication on port 5000
- **Entry Point**: `index.js`
- **Static Files**: Served from `src/dashboard/static/` with support for HTML, CSS, JS, JSX, TS, TSX, JSON, images
- **Authentication**: Discord OAuth2 with `/login`, `/profile`, `/logout` routes
- **Features**: Premium dashboard UI, Stripe payment integration (TEST mode)

### Dashboard (Premium UI)
- **Location**: `src/dashboard/index.html`
- **Features**: 
  - Discord "Sign in with Discord" button with OAuth login flow
  - Feature showcase (76+ commands, moderation, fun utilities, real-time stats)
  - Stripe integration for $9.99 Premium subscription
  - Flask backend at `src/dashboard/app.py` for payment processing
  - System stats API endpoint at `/api/stats`

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
| `bot.py` | Discord bot (2130 lines) with 76+ slash commands, moderation, fun utilities, and event handlers |
| `index.js` | Express web server with Passport Discord OAuth, dashboard serving, and static file handling (HTML/CSS/JS/TS/TSX) |
| `src/dashboard/index.html` | Premium dashboard landing page with Discord login button and feature showcase |
| `src/dashboard/app.py` | Flask backend for Stripe payment processing and system stats API |
| `src/dashboard/templates/index.html` | Stripe checkout template |
| `src/dashboard/static/style.css` | Premium dashboard styles |
| `.env` | Environment variables: DISCORD_TOKEN, CLIENT_ID, CLIENT_SECRET, STRIPE_PUBLISHABLE_KEY, STRIPE_SECRET_KEY |

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