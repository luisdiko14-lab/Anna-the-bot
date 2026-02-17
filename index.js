// index.js (ES module)
import dotenv from 'dotenv';
dotenv.config();

import express from 'express';
import session from 'express-session';
import passport from 'passport';
import { Strategy as DiscordStrategy } from 'passport-discord';
import path from 'path';
import { fileURLToPath } from 'url';

import {
  Client,
  GatewayIntentBits,
  Partials,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  ChannelType,
  SlashCommandBuilder,
  EmbedBuilder,
  ActivityType,
} from 'discord.js';

import { REST } from '@discordjs/rest';
import { Routes } from 'discord-api-types/v10';
import { GoogleGenerativeAI } from '@google/generative-ai';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/* ---------------------------
   Basic config & checks
   --------------------------- */
const DISCORD_TOKEN = process.env.DISCORD_TOKEN;
const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;
const CALLBACK_URL = 'https://853cb505-0e22-49ec-b716-48bb6375c8aa-00-4jll9e93a7pf.janeway.replit.dev/api/callback';
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

if (!DISCORD_TOKEN) {
  console.error('Missing DISCORD_TOKEN in .env');
  process.exit(1);
}

/* ---------------------------
   Express & Passport Setup
   --------------------------- */
const app = express();
const port = 5000;

passport.serializeUser((user, done) => done(null, user));
passport.deserializeUser((obj, done) => done(null, obj));

passport.use(new DiscordStrategy({
    clientID: CLIENT_ID,
    clientSecret: CLIENT_SECRET,
    callbackURL: CALLBACK_URL,
    scope: ['identify', 'email']
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

app.set('view engine', 'html');
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

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
                    <img src="https://cdn.discordapp.com/avatars/${req.user.id}/${req.user.avatar}.png" width="128">
                    <h1>Welcome, ${req.user.username}!</h1>
                    <p>Logged in via Discord Auth</p>
                    <p>Email: ${req.user.email}</p>
                    <a href="/">Back to Home</a>
                    <a href="/logout" style="border-color: #ff4444; color: #ff4444;">Logout</a>
                </div>
            </body>
        </html>
    `);
});

app.get('/logout', (req, res) => {
    req.logout(() => {
        res.redirect('/');
    });
});

app.listen(port, '0.0.0.0', () => {
    console.log(`Web server running at http://0.0.0.0:${port}`);
});

/* ---------------------------
   Discord client
   --------------------------- */
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
  partials: [Partials.Channel],
});

/* ---------------------------
   Generative AI client + helpers
   --------------------------- */
const genAI = GEMINI_API_KEY ? new GoogleGenerativeAI(GEMINI_API_KEY) : null;
let flashModel = null;
let selectedModelId = null;

const MODEL_CANDIDATES = [
  'gemini-1.5-flash',
  'gemini-1.5-flash-lite',
  'gemini-1.5-pro',
  'gemini-2.0-flash',
  'text-bison-001',
];

function extractTextFromAIResult(result) {
  try {
    if (!result) return null;
    if (result.response && typeof result.response.text === 'function') return result.response.text();
    if (result.response && typeof result.response.text === 'string') return result.response.text;
    if (typeof result.outputText === 'string') return result.outputText;
    if (typeof result === 'string') return result;
    if (Array.isArray(result.candidates) && result.candidates[0]) {
      if (typeof result.candidates[0].text === 'string') return result.candidates[0].text;
      if (typeof result.candidates[0].output === 'string') return result.candidates[0].output;
    }
    return null;
  } catch (e) {
    return null;
  }
}

function truncateForDiscord(s, max = 1900) {
  if (!s) return s;
  return s.length > max ? (s.slice(0, max) + "\n\n...(truncated)") : s;
}

async function safeGenerate(prompt) {
  if (!prompt) return null;
  if (!genAI) throw new Error('Generative AI client not initialized (GEMINI_API_KEY missing).');
  if (!flashModel) await initFlashModel();
  if (!flashModel) throw new Error('No Gemini model available');

  const res = await flashModel.generateContent(prompt);
  return extractTextFromAIResult(res) || null;
}

async function initFlashModel() {
  if (!genAI) {
    flashModel = null;
    selectedModelId = null;
    return;
  }

  for (const candidate of MODEL_CANDIDATES) {
    try {
      console.log(`Trying Gemini model candidate: ${candidate}`);
      const m = genAI.getGenerativeModel({ model: candidate });
      const testRes = await m.generateContent('Hello');
      const txt = extractTextFromAIResult(testRes);
      if (txt && txt.length > 0) {
        flashModel = m;
        selectedModelId = candidate;
        console.log(`Selected Gemini model: ${candidate}`);
        return;
      }
    } catch (err) {
      console.warn(`Candidate ${candidate} failed.`);
    }
  }

  flashModel = null;
  selectedModelId = null;
}

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
  new SlashCommandBuilder().setName('startconversation').setDescription('Start a Gemini conversation (creates a thread with interactive buttons)'),
  new SlashCommandBuilder()
    .setName('prompt')
    .setDescription('Send a prompt to Gemini Flash and get a direct reply')
    .addStringOption((option) => option.setName('message').setDescription('Your prompt for the AI').setRequired(true)),
].map((c) => c.toJSON());

async function registerCommands(applicationId) {
  try {
    const rest = new REST({ version: '10' }).setToken(DISCORD_TOKEN);
    await rest.put(Routes.applicationCommands(applicationId), { body: commands });
    console.log('Commands registered.');
  } catch (err) {
    console.error('Failed to register slash commands:', err);
  }
}

const activatedGuilds = new Set();
const activeThreads = new Map();
const threadLastUserMessage = new Map();
const annaCooldown = new Map();

client.once('ready', async () => {
  console.log(`Logged in as ${client.user.tag} (${client.user.id})`);
  const applicationId = CLIENT_ID || client.user.id;
  await registerCommands(applicationId);
  await initFlashModel();

  const statuses = [
    { name: 'with Gemini', type: ActivityType.Playing },
    { name: 'Helping people', type: ActivityType.Playing },
  ];

  let index = 0;
  setInterval(() => {
    index = (index + 1) % statuses.length;
    try {
      client.user.setPresence({ activities: [statuses[index]], status: 'online' });
    } catch (e) {}
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
      if (name === 'startconversation') {
        return interaction.reply({ content: '✨ Choose a model to start a conversation.', flags: [4096] });
      }
      if (name === 'prompt') {
        const userPrompt = interaction.options.getString('message', true).trim();
        await interaction.deferReply({ flags: [4096] });
        try {
          const resultText = await safeGenerate(userPrompt);
          const responseText = truncateForDiscord(resultText || '⛔ Could not extract a reply.');
          const outEmbed = new EmbedBuilder().setTitle(`Gemini • ${selectedModelId || 'flash'}`).setDescription(responseText);
          await postVisible(interaction.channel, responseText, outEmbed);
          return interaction.editReply({ content: '✅ Posted reply to the channel.', embeds: [outEmbed] });
        } catch (err) {
          return interaction.editReply('❌ Failed to get a response.');
        }
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

    if (activeThreads.has(message.channel.id)) {
      const userPrompt = message.content?.trim();
      if (!userPrompt || userPrompt.startsWith('/')) return;
      await message.channel.sendTyping();
      const responseText = await safeGenerate(userPrompt);
      await message.reply(truncateForDiscord(responseText || '⛔ No reply.'));
    }
  } catch (err) {}
});

client.login(DISCORD_TOKEN);
