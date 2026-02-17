// index.js (ES module) — improved, more robust, buttons post visible replies to the conversation
import dotenv from 'dotenv';
dotenv.config();

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

/* ---------------------------
   Basic config & checks
   --------------------------- */
const DISCORD_TOKEN = process.env.DISCORD_TOKEN;
const CLIENT_ID = process.env.CLIENT_ID;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

if (!DISCORD_TOKEN) {
  console.error('Missing DISCORD_TOKEN in .env');
  process.exit(1);
}
if (!CLIENT_ID) console.warn('CLIENT_ID not set — registering global commands will fall back to bot user id');
if (!GEMINI_API_KEY) console.warn('GEMINI_API_KEY not set. AI features will be unavailable until you set it.');

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
  'gemini-2.5-flash',
  'gemini-2.5-flash-lite',
  'gemini-2.5-pro',
  'gemini-2.0-flash',
  'text-bison-001',
];

function extractTextFromAIResult(result) {
  try {
    if (!result) return null;
    // Common shapes: { response: { text: '...' } } or { outputText: '...' } or SDK objects
    if (result.response && typeof result.response.text === 'function') return result.response.text();
    if (result.response && typeof result.response.text === 'string') return result.response.text;
    if (typeof result.outputText === 'string') return result.outputText;
    if (typeof result === 'string') return result;

    // SDKs sometimes return candidates or output arrays
    if (Array.isArray(result.candidates) && result.candidates[0]) {
      if (typeof result.candidates[0].text === 'string') return result.candidates[0].text;
      if (typeof result.candidates[0].output === 'string') return result.candidates[0].output;
    }

    if (result.output && Array.isArray(result.output) && result.output[0]) {
      const obj = result.output[0];
      if (typeof obj.content === 'string') return obj.content;
      if (Array.isArray(obj.content) && obj.content[0] && obj.content[0].text) return obj.content[0].text;
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
    console.warn('genAI client not initialized (no GEMINI_API_KEY).');
    flashModel = null;
    selectedModelId = null;
    return;
  }

  for (const candidate of MODEL_CANDIDATES) {
    try {
      console.log(`Trying Gemini model candidate: ${candidate}`);
      const m = genAI.getGenerativeModel({ model: candidate });
      // smoke test
      const testRes = await m.generateContent('Hello');
      const txt = extractTextFromAIResult(testRes);
      if (txt && txt.length > 0) {
        flashModel = m;
        selectedModelId = candidate;
        console.log(`Selected Gemini model: ${candidate}`);
        return;
      }
      console.warn(`Candidate ${candidate} returned no usable text; trying next.`);
    } catch (err) {
      const status = err?.status || err?.statusCode || (err?.response && err.response.status);
      console.warn(`Candidate ${candidate} failed: ${status || (err && err.message) || String(err)}`);
    }
  }

  flashModel = null;
  selectedModelId = null;
  console.error('No viable Gemini model found. Check GEMINI_API_KEY and MODEL_CANDIDATES.');
}

/* ---------------------------
   Helpers for visible posting
   --------------------------- */
async function postVisible(channel, content, embed = null) {
  try {
    if (!channel) throw new Error('Channel missing');
    const payload = {};
    if (embed) payload.embeds = [embed];
    if (content) payload.content = content;
    return await channel.send(payload);
  } catch (err) {
    console.error('postVisible error:', err);
    throw err;
  }
}

/* ---------------------------
   Slash commands
   --------------------------- */
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
    console.log('Registering application commands...');
    await rest.put(Routes.applicationCommands(applicationId), { body: commands });
    console.log('Commands registered.');
  } catch (err) {
    console.error('Failed to register slash commands:', err);
  }
}

/* ---------------------------
   State
   --------------------------- */
const activatedGuilds = new Set();
const activeThreads = new Map(); // threadId -> modelId
const threadLastUserMessage = new Map(); // threadId -> last user message content
const annaCooldown = new Map(); // userId -> timestamp

/* ---------------------------
   Ready
   --------------------------- */
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
  try {
    await client.user.setPresence({ activities: [statuses[index]], status: 'idle' });
  } catch (e) {
    console.warn('Setting presence failed:', e?.message || e);
  }

  setInterval(() => {
    index = (index + 1) % statuses.length;
    try {
      client.user.setPresence({ activities: [statuses[index]], status: 'online' });
    } catch (e) {
      console.warn('Presence rotate failed:', e?.message || e);
    }
  }, 15_000);
});

/* ---------------------------
   Buttons builder (visible to everyone)
   --------------------------- */
function buildConversationButtons(interactionUser) {
  const allowedUsers = ['luisthegoat7301', 'zelda_life', 'blackopsmode'];
  const isAllowed = allowedUsers.includes(interactionUser.username);

  const primaryRow = new ActionRowBuilder().addComponents(
    new ButtonBuilder().setCustomId('gemini_flash').setLabel('Gemini Flash').setStyle(ButtonStyle.Primary),
    new ButtonBuilder().setCustomId('gemini_pro').setLabel('Gemini Pro').setStyle(ButtonStyle.Secondary).setDisabled(true),
    new ButtonBuilder().setCustomId('gemini_ultimate').setLabel('Gemini Ultimate').setStyle(ButtonStyle.Success).setDisabled(!isAllowed),
    new ButtonBuilder().setCustomId('gemini_expert').setLabel('Gemini Expert').setStyle(ButtonStyle.Danger).setDisabled(!isAllowed)
  );

  const utilRow = new ActionRowBuilder().addComponents(
    new ButtonBuilder().setCustomId('summarize').setLabel('Summarize').setStyle(ButtonStyle.Secondary),
    new ButtonBuilder().setCustomId('translate').setLabel('Translate → EN').setStyle(ButtonStyle.Secondary),
    new ButtonBuilder().setCustomId('regenerate').setLabel('Regenerate Reply').setStyle(ButtonStyle.Primary),
    new ButtonBuilder().setCustomId('stop_convo').setLabel('Stop / Close Thread').setStyle(ButtonStyle.Danger),
    new ButtonBuilder().setCustomId('pin_convo').setLabel('Pin Last Reply').setStyle(ButtonStyle.Success)
  );

  return [primaryRow, utilRow];
}

/* ---------------------------
   Interaction handling
   --------------------------- */
client.on('interactionCreate', async (interaction) => {
  try {
    if (interaction.isChatInputCommand()) {
      const name = interaction.commandName;

      if (name === 'activate') {
        if (!interaction.guild) return interaction.reply({ content: 'This command must be used in a server.', ephemeral: true });
        activatedGuilds.add(interaction.guild.id);
        return interaction.reply({ content: '✅ Activation enabled — I will respond when someone mentions **Anna**.', ephemeral: true });
      }

      if (name === 'startconversation') {
        const rows = buildConversationButtons(interaction.user);
        return interaction.reply({ content: '✨ Choose a model / option to start a conversation (buttons are visible to everyone).', components: rows, ephemeral: false });
      }

      if (name === 'prompt') {
        const userPrompt = interaction.options.getString('message', true).trim();
        if (!userPrompt) return interaction.reply({ content: 'Please provide a prompt.', ephemeral: true });

        await interaction.deferReply({ ephemeral: true });
        try {
          const resultText = await safeGenerate(userPrompt);
          const responseText = truncateForDiscord(resultText || '⛔ Could not extract a reply.');
          const outEmbed = new EmbedBuilder().setTitle(`Gemini • ${selectedModelId || 'flash'}`).setDescription(responseText).setFooter({ text: `Requested by ${interaction.user.tag}` }).setTimestamp();

          // Post the result visibly to the channel where the command was used
          await postVisible(interaction.channel, responseText, outEmbed).catch(() => null);

          // Send ephemeral confirmation to the command user with the embed
          return interaction.editReply({ content: '✅ Posted reply to the channel.', embeds: [outEmbed] });
        } catch (err) {
          console.error('Error calling Gemini (prompt):', err);
          return interaction.editReply('❌ Failed to get a response from Gemini.');
        }
      }
      return;
    }

    if (interaction.isButton()) {
      const id = interaction.customId;
      const allowedUsers = ['luisthegoat7301', 'zelda_life', 'blackopsmode'];
      const isAllowed = allowedUsers.includes(interaction.user.username);

      // Model buttons: create public thread (visible to all)
      if (id.startsWith('gemini_')) {
        if ((id === 'gemini_ultimate' || id === 'gemini_expert') && !isAllowed) {
          return interaction.reply({ content: '❌ You are not authorized to use this model.', ephemeral: true });
        }

        const channel = interaction.channel;
        if (!channel || !interaction.guild) return interaction.reply({ content: "Can't create a thread here.", ephemeral: true });

        try {
          const thread = await channel.threads.create({ name: `${id}-${interaction.user.username}`.slice(0, 100), type: ChannelType.PublicThread, autoArchiveDuration: 1440 });

          activeThreads.set(thread.id, id);
          threadLastUserMessage.set(thread.id, null);

          const starterEmbed = new EmbedBuilder().setTitle(`Gemini • ${id.replace('gemini_', '').toUpperCase()} Thread`).setDescription('💬 Welcome! Type prompts here and the bot will reply using Gemini AI.').addFields({ name: 'Tip', value: 'Short, clear prompts get better results!' }).setFooter({ text: `Thread created by ${interaction.user.tag}` }).setTimestamp();

          await postVisible(thread, `Hello <@${interaction.user.id}> — I'll reply to prompts here using ${selectedModelId || 'the configured model'}.`, starterEmbed);

          await interaction.reply({ content: `🧵 Thread created: <#${thread.id}> — join the conversation!`, ephemeral: false });
        } catch (err) {
          console.error('Failed to create thread:', err);
          await interaction.reply({ content: '❌ Failed to create a thread.', ephemeral: true });
        }
        return;
      }

      // Utility buttons operate on the current channel (prefer thread context)
      const channel = interaction.channel;
      const inThread = typeof channel?.isThread === 'function' ? channel.isThread() : false;
      const threadId = channel?.id;

      if (id === 'summarize') {
        if (!inThread || !activeThreads.has(threadId)) {
          return interaction.reply({ content: '🔎 Summarize works inside an active conversation thread.', ephemeral: true });
        }

        await interaction.deferReply({ ephemeral: true });
        try {
          const msgs = await channel.messages.fetch({ limit: 20 });
          const userTexts = msgs.filter((m) => !m.author.bot).map((m) => m.content).reverse().join('\n\n');
          const prompt = `Summarize the following conversation in 2-4 short bullet points:\n\n${userTexts}`;
          const summary = await safeGenerate(prompt);

          if (summary) {
            const visible = `**Summary:**\n${truncateForDiscord(summary, 1900)}`;
            await postVisible(channel, visible);
            return interaction.editReply({ content: '✅ Summary posted to the thread/channel.' });
          }

          return interaction.editReply('❌ Could not summarize.');
        } catch (err) {
          console.error('Summarize error:', err);
          return interaction.editReply('❌ Failed to summarize conversation.');
        }
      }

      if (id === 'translate') {
        if (!inThread || !activeThreads.has(threadId)) {
          return interaction.reply({ content: '🌐 Translate works inside an active conversation thread.', ephemeral: true });
        }

        await interaction.deferReply({ ephemeral: true });
        try {
          const msgs = await channel.messages.fetch({ limit: 12 });
          const target = msgs.find((m) => !m.author.bot && m.content)?.content;
          if (!target) return interaction.editReply('❌ No user message found to translate.');

          const prompt = `Translate the following text to clear, idiomatic English:\n\n${target}`;
          const out = await safeGenerate(prompt);

          if (out) {
            const visible = `**Translation:**\n${truncateForDiscord(out)}`;
            await postVisible(channel, visible);
            return interaction.editReply({ content: '✅ Translation posted to the thread/channel.' });
          }

          return interaction.editReply('❌ Could not translate.');
        } catch (err) {
          console.error('Translate error:', err);
          return interaction.editReply('❌ Failed to translate.');
        }
      }

      if (id === 'regenerate') {
        if (!inThread || !activeThreads.has(threadId)) {
          return interaction.reply({ content: '🔁 Regenerate works inside an active conversation thread.', ephemeral: true });
        }

        await interaction.deferReply({ ephemeral: true });
        try {
          let last = threadLastUserMessage.get(threadId);
          if (!last) {
            const msgs = await channel.messages.fetch({ limit: 20 });
            last = msgs.filter((m) => !m.author.bot).first()?.content;
          }
          if (!last) return interaction.editReply('❌ No recent user message to regenerate for.');

          const prompt = `Please provide another response to the user's message below (brief):\n\nUser: ${last}`;
          const out = await safeGenerate(prompt);

          if (out) {
            await postVisible(channel, truncateForDiscord(out));
            return interaction.editReply({ content: '✅ Regenerated reply posted to the thread.' });
          }

          return interaction.editReply('❌ Could not generate a reply.');
        } catch (err) {
          console.error('Regenerate error:', err);
          return interaction.editReply('❌ Failed to regenerate.');
        }
      }

      if (id === 'stop_convo') {
        if (!inThread || !activeThreads.has(threadId)) {
          return interaction.reply({ content: '❌ Stop works inside an active conversation thread.', ephemeral: true });
        }

        // only thread creator or allowed users can stop
        const starterMessage = await channel.fetchStarterMessage().catch(() => null);
        const starterId = starterMessage?.author?.id;
        const isStarter = starterId === interaction.user.id;
        if (!isStarter && !allowedUsers.includes(interaction.user.username)) {
          return interaction.reply({ content: '❌ Only the thread starter or an admin can stop this conversation.', ephemeral: true });
        }

        try {
          activeThreads.delete(threadId);
          threadLastUserMessage.delete(threadId);
          await postVisible(channel, '⛔ Conversation closed by request. Archiving thread...');
          await channel.setArchived(true);
          return interaction.reply({ content: '✅ Thread archived.', ephemeral: false });
        } catch (err) {
          console.error('Stop convo error:', err);
          return interaction.reply({ content: '❌ Failed to stop/archive the thread.', ephemeral: true });
        }
      }

      if (id === 'pin_convo') {
        if (!inThread || !activeThreads.has(threadId)) {
          return interaction.reply({ content: '📌 Pin works inside an active conversation thread.', ephemeral: true });
        }

        try {
          const msgs = await channel.messages.fetch({ limit: 40 });
          const botMsg = msgs.find((m) => m.author?.id === client.user.id);
          if (!botMsg) return interaction.reply({ content: '❌ No bot message found to pin.', ephemeral: true });
          await botMsg.pin();
          await interaction.reply({ content: '📌 Pinned the last bot reply.', ephemeral: false });
        } catch (err) {
          console.error('Pin error:', err);
          return interaction.reply({ content: '❌ Failed to pin message.', ephemeral: true });
        }
      }

      // unknown button fallback
      return interaction.reply({ content: '❌ Unknown button.', ephemeral: true });
    }
  } catch (err) {
    console.error('Interaction handler error:', err);
    try {
      if (interaction && !interaction.replied && !interaction.deferred) {
        await interaction.reply({ content: '❌ An error occurred while handling that interaction.', ephemeral: true });
      }
    } catch {}
  }
});

/* ---------------------------
   Message create (Anna auto-reply + thread AI)
   --------------------------- */
client.on('messageCreate', async (message) => {
  try {
    if (message.author?.bot) return;
    if (!message.guild) return;

    // ANNA auto-reply (visible publicly)
    if (activatedGuilds.has(message.guild.id) && /anna/i.test(message.content)) {
      const now = Date.now();
      const last = annaCooldown.get(message.author.id) || 0;
      const COOLDOWN_MS = 6_000; // 6s per user throttle
      if (now - last < COOLDOWN_MS) return;
      annaCooldown.set(message.author.id, now);

      await message.channel.sendTyping();
      await new Promise((r) => setTimeout(r, 900));
      await postVisible(message.channel, `👋 <@${message.author.id}> you mentioned Anna — here's what you said:\n> ${message.content}`, null);
    }

    // Thread AI reply
    const channelId = message.channel.id;
    if (activeThreads.has(channelId)) {
      const userPrompt = message.content?.trim();
      if (!userPrompt || userPrompt.startsWith('/')) return;

      // track last user message for regenerate and utilities
      threadLastUserMessage.set(channelId, userPrompt);

      if (!genAI) return message.channel.send('❌ Gemini not configured (GEMINI_API_KEY missing).');
      if (!flashModel) await initFlashModel();
      if (!flashModel) return message.channel.send('❌ Gemini not initialized.');

      await message.channel.sendTyping();
      try {
        const responseText = await safeGenerate(userPrompt);
        const final = truncateForDiscord(responseText || '⛔ Could not extract a reply.');
        // reply publicly in-thread (visible)
        await message.reply(final);
      } catch (err) {
        console.error('Thread Gemini error:', err);
        await message.reply('❌ Failed to get a response from Gemini.');
      }
    }
  } catch (err) {
    console.error('messageCreate error:', err);
  }
});

/* ---------------------------
   Global error handlers & login
   --------------------------- */
process.on('unhandledRejection', (reason) => {
  console.error('Unhandled Rejection:', reason);
});
process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
});

client.login(DISCORD_TOKEN).catch((err) => {
  console.error('Failed to login:', err);
  process.exit(1);
});
