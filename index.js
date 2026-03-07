// index.js (ES module) — fixed serving of dashboard and env var typo
import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import session from 'express-session';
import passport from 'passport';
import { Strategy as DiscordStrategy } from 'passport-discord';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

import {
  Client,
  GatewayIntentBits,
  Partials,
  SlashCommandBuilder,
  ActivityType,
} from 'discord.js';

import { REST } from '@discordjs/rest';
import { Routes } from 'discord-api-types/v10';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/* ---------------------------
   Basic config
   --------------------------- */
// Use the correct env var name
const DISCORD_TOKEN = process.env.DISCORD_TOKEN || null;
const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;
// keep your existing callback URL or set via env
const CALLBACK_URL = process.env.CALLBACK_URL || 'https://853cb505-0e22-49ec-b716-48bb6375c8aa-00-4jll9e93a7pf.janeway.replit.dev/api/callback';

/* ---------------------------
   Express & Passport Setup
   --------------------------- */
const app = express();
const port = process.env.PORT || 5000;

passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((obj, done) => done(null, obj));

passport.use(new DiscordStrategy({
    clientID: CLIENT_ID,
    clientSecret: CLIENT_SECRET,
    callbackURL: CALLBACK_URL,
    scope: ['identify', 'email', 'guilds', 'guilds.join', 'guilds.members.read']
}, (accessToken, refreshToken, profile, done) => {
    process.nextTick(() => done(null, profile));
}));

app.use(session({
    secret: 'anna-bot-secret',
    resave: false,
    saveUninitialized: false
}));

app.use(passport.initialize());
app.use(passport.session());

/* ---------------------------
   Static / Dashboard serving
   Allow: HTML, CSS, JS, JSX, TS, TSX, JSON, PNG, JPG, SVG, etc.
   --------------------------- */
// Serve static files with all common extensions
const staticPath = path.join(__dirname, 'src', 'dashboard', 'static');
app.use(express.static(staticPath, {
    setHeaders: (res, filePath) => {
        // Serve TypeScript/TSX files as JavaScript
        if (filePath.endsWith('.tsx') || filePath.endsWith('.ts')) {
            res.setHeader('Content-Type', 'application/javascript');
        }
        // Cache control
        res.setHeader('Cache-Control', 'public, max-age=3600');
    }
}));

// Serve dashboard index.html as the SPA entrypoint
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'src', 'dashboard', 'index.html'));
});

// Serve other HTML files from src/dashboard/
app.get('/:file.html', (req, res) => {
    const filePath = path.join(__dirname, 'src', 'dashboard', req.params.file + '.html');
    if (fs.existsSync(filePath)) {
        res.sendFile(filePath);
    } else {
        res.status(404).send('File not found');
    }
});
// -------------------------------------------------------

app.get('/login', passport.authenticate('discord'));

app.get('/api/callback', passport.authenticate('discord', {
    failureRedirect: '/'
}), (req, res) => {
    res.redirect('/profile');
});

app.get('/profile', (req, res) => {
    if (!req.isAuthenticated()) return res.redirect('/login');
    res.send(`
        <html>
            <head>
                <title>Anna Bot Profile</title>
                <style>
                    body { background: #0a0f1f; color: white; font-family: sans-serif; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; margin: 0; }
                    .card { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; text-align: center; box-shadow: 0 0 20px rgba(0,170,255,0.2); }
                    img { border-radius: 50%; border: 3px solid #00b7ff; margin-bottom: 20px; }
                    h1 { margin: 0; color: #00b7ff; }
                    p { opacity: 0.8; }
                    a { color: #00b7ff; text-decoration: none; margin-top: 20px; display: inline-block; border: 1px solid #00b7ff; padding: 10px 20px; border-radius: 10px; transition: 0.3s; }
                    a:hover { background: #00b7ff; color: white; }
                </style>
            </head>
            <body>
                <div class="card">
                    <img src="https://cdn.discordapp.com/avatars/${req.user.id}/${req.user.avatar}.png" width="128" />
                    <h1>Welcome, ${req.user.username}!</h1>
                    <p>Logged in via Discord Auth</p>
                    <p>Email: ${req.user.email || '—'}</p>
                    <p style="margin-top:16px;">
                      <a href="/">Back to Home</a>
                      <a href="/logout" style="margin-left:12px; border-color: #ff4444; color: #ff4444;">Logout</a>
                    </p>
                </div>
            </body>
        </html>
    `);
});

app.get('/logout', (req, res, next) => {
    // passport 0.6+ expects a callback: req.logout(cb)
    req.logout(function(err) {
      if (err) { return next(err); }
      res.redirect('/');
    });
});

app.listen(port, '0.0.0.0', () => {
    console.log(`Web server running at http://0.0.0.0:${port}`);
});

/* ---------------------------
   Discord client (minimal)
   --------------------------- */
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
  partials: [Partials.Channel],
});

async function postVisible(channel, content, embed = null) {
  try {
    const payload = {};
    if (embed) payload.embeds = [embed];
    if (content) payload.content = content;
    return await channel.send(payload);
  } catch (err) {
    console.error('postVisible error:', err);
    throw err;
  }
}

const commands = [
  new SlashCommandBuilder().setName('activate').setDescription('Activate Anna auto-response in this server'),
].map((c) => c.toJSON());

async function registerCommands(applicationId) {
  if (!DISCORD_TOKEN) {
    console.log('DISCORD_TOKEN not set — skipping slash command registration.');
    return;
  }
  try {
    const rest = new REST({ version: '10' }).setToken(DISCORD_TOKEN);
    await rest.put(Routes.applicationCommands(applicationId), { body: commands });
    console.log('Commands registered.');
  } catch (err) {
    console.error('Failed to register slash commands:', err);
  }
}

const activatedGuilds = new Set();

client.once('ready', async () => {
  console.log(`Logged in as ${client.user.tag} (${client.user.id})`);
  const applicationId = CLIENT_ID || client.user.id;
  await registerCommands(applicationId);

  const statuses = [
    { name: 'Helping people', type: ActivityType.Playing },
    { name: 'Anna Bot', type: ActivityType.Playing },
  ];

  let index = 0;
  setInterval(() => {
    index = (index + 1) % statuses.length;
    try {
      client.user.setPresence({ activities: [statuses[index]], status: 'online' });
    } catch (e) {
      // ignore
    }
  }, 15_000);
});

client.on('interactionCreate', async (interaction) => {
  try {
    if (interaction.isChatInputCommand()) {
      const name = interaction.commandName;
      if (name === 'activate') {
        if (!interaction.guild) return interaction.reply({ content: 'This command must be used in a server.', flags: [4096] });
        activatedGuilds.add(interaction.guild.id);
        return interaction.reply({ content: '✅ Activation enabled.', flags: [4096] });
      }
    }
  } catch (err) {
    console.error('Interaction handler error:', err);
  }
});

client.on('messageCreate', async (message) => {
  try {
    if (message.author?.bot) return;
    if (!message.guild) return;

    if (activatedGuilds.has(message.guild.id) && /anna/i.test(message.content)) {
      await message.channel.sendTyping();
      await postVisible(message.channel, `👋 <@${message.author.id}> you mentioned Anna!`, null);
    }
  } catch (err) {
    console.error('messageCreate handler error:', err);
  }
});

if (DISCORD_TOKEN) {
  client.login(DISCORD_TOKEN).catch((err) => {
    console.error('Failed to login to Discord:', err);
  });
} else {
  console.log('DISCORD_TOKEN not provided — Discord client will not login. OAuth (web) still works.');
}