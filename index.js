// index.js (ES module) -- fallback-capable Gemini model initialization
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
} from 'discord.js';

import { REST } from '@discordjs/rest';
import { Routes } from 'discord-api-types/v10';

import { GoogleGenerativeAI } from '@google/generative-ai';

const DISCORD_TOKEN = process.env.DISCORD_TOKEN;
const CLIENT_ID = process.env.CLIENT_ID;
const GEMINI_API_KEY = process.env.GEMINI_API_KEY;

if (!DISCORD_TOKEN) {
  console.error("Missing DISCORD_TOKEN in .env");
  process.exit(1);
}

if (!GEMINI_API_KEY) {
  console.warn("Warning: GEMINI_API_KEY not set. AI features will be unavailable until you set it.");
}

/* ===========================
   Discord client
=========================== */
const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
  partials: [Partials.Channel]
});

/* ===========================
   Google Gemini (genAI) & model state
=========================== */
const genAI = GEMINI_API_KEY ? new GoogleGenerativeAI(GEMINI_API_KEY) : null;
let flashModel = null; // will hold a working model object (from genAI.getGenerativeModel)
let selectedModelId = null; // string name of selected model in use

// Candidate model IDs to try, in preference order.
// Update this list if you want to force a particular model.
// Current reasonable choices: gemini-2.5-flash, gemini-2.5-flash-lite, gemini-2.5-pro, fallback text-bison
const MODEL_CANDIDATES = [
  'gemini-2.5-flash',
  'gemini-2.5-flash-lite',
  'gemini-2.5-pro',
  'gemini-2.0-flash',
  'text-bison-001' // older / fallback model
];

/* ===========================
   Utilities
=========================== */
function extractTextFromAIResult(result) {
  try {
    if (!result) return null;
    if (result.response && typeof result.response.text === 'function') {
      return result.response.text();
    }
    if (result.response && typeof result.response.text === 'string') {
      return result.response.text;
    }
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

/* ===========================
   Initialize / Pick a working model
   - Tries each candidate model until generateContent succeeds
   - Logs selected model to console
=========================== */
async function initFlashModel() {
  if (!genAI) {
    console.warn("genAI client not initialized (no GEMINI_API_KEY).");
    flashModel = null;
    selectedModelId = null;
    return;
  }

  for (const candidate of MODEL_CANDIDATES) {
    try {
      console.log(`Trying Gemini model candidate: ${candidate}`);
      // get the model wrapper object
      const m = genAI.getGenerativeModel({ model: candidate });

      // Try a light-weight health-check generation to ensure the model supports generateContent.
      // Keep this prompt tiny to avoid heavy usage.
      const testPrompt = "Hello";
      const testRes = await m.generateContent(testPrompt);

      const txt = extractTextFromAIResult(testRes);
      if (txt && txt.length > 0) {
        flashModel = m;
        selectedModelId = candidate;
        console.log(`Selected Gemini model: ${candidate}`);
        return;
      } else {
        console.warn(`Candidate ${candidate} returned but no usable text extracted; trying next.`);
      }
    } catch (err) {
      // If 404, the model alias probably isn't available under this API/version; try next.
      const status = err?.status || err?.statusCode || (err?.response && err.response.status);
      console.warn(`Candidate ${candidate} failed: ${status || err.message || String(err)}`);
      // continue to next candidate
    }
  }

  // If we reach here, none of the candidates worked.
  flashModel = null;
  selectedModelId = null;
  console.error("No viable Gemini model found. Check GEMINI_API_KEY, available models in your region, or update MODEL_CANDIDATES.");
}

/* ===========================
   Slash commands
=========================== */
const commands = [
  new SlashCommandBuilder()
    .setName('activate')
    .setDescription('Activate Anna auto-response in this server'),

  new SlashCommandBuilder()
    .setName('startconversation')
    .setDescription('Start a Gemini conversation (creates thread with a button)'),

  new SlashCommandBuilder()
    .setName('prompt')
    .setDescription('Send a prompt to Gemini Flash and get a direct reply')
    .addStringOption(option =>
      option.setName('message')
        .setDescription('Your prompt for the AI')
        .setRequired(true)
    )
].map(cmd => cmd.toJSON());

const registerCommands = async (applicationId) => {
  try {
    const rest = new REST({ version: '10' }).setToken(DISCORD_TOKEN);
    console.log("Registering application commands...");
    await rest.put(Routes.applicationCommands(applicationId), { body: commands });
    console.log("Commands registered.");
  } catch (err) {
    console.error("Failed to register slash commands:", err);
  }
};

/* ===========================
   State containers (Anna + threads)
=========================== */
const activatedGuilds = new Set();   // guild IDs where Anna auto-response is enabled
const activeThreads = new Map();     // threadId -> modelType ('flash', ...)

/* ===========================
   Ready
=========================== */
client.once('ready', async () => {
  console.log(`Logged in as ${client.user.tag} (${client.user.id})`);
  const applicationId = CLIENT_ID || client.user.id;
  await registerCommands(applicationId);

  // Initialize a working Gemini model (attempt candidates)
  await initFlashModel();
});

/* ===========================
   Interaction Handler (slash & buttons)
=========================== */
client.on('interactionCreate', async (interaction) => {
  try {
    if (interaction.isChatInputCommand && interaction.isChatInputCommand()) {
      const name = interaction.commandName;

      if (name === 'activate') {
        if (!interaction.guild) return interaction.reply({ content: "This command must be used in a server (guild).", ephemeral: true });
        activatedGuilds.add(interaction.guild.id);
        return interaction.reply({ content: "✅ Activation enabled — I will respond when someone mentions **Anna** in this server.", ephemeral: true });
      }

      if (name === 'startconversation') {
        const row = new ActionRowBuilder().addComponents(
          new ButtonBuilder()
            .setCustomId('gemini_flash')
            .setLabel('Gemini Flash')
            .setStyle(ButtonStyle.Primary),

          new ButtonBuilder()
            .setCustomId('gemini_pro')
            .setLabel('Gemini Pro (soon)')
            .setStyle(ButtonStyle.Secondary)
            .setDisabled(true)
        );

        return interaction.reply({
          content: "✨ Choose a model to start a conversation. (Click a button to create a thread for the AI.)",
          components: [row],
          ephemeral: true
        });
      }

      if (name === 'prompt') {
        const userPrompt = interaction.options.getString('message', true).trim();
        if (!userPrompt) return interaction.reply({ content: "Please provide a prompt.", ephemeral: true });

        await interaction.deferReply({ ephemeral: false });

        if (!flashModel) {
          // Try re-initializing once before failing
          await initFlashModel();
          if (!flashModel) {
            await interaction.editReply("❌ No Gemini model is initialized. Check GEMINI_API_KEY and model availability.");
            return;
          }
        }

        try {
          const result = await flashModel.generateContent(userPrompt);
          let responseText = extractTextFromAIResult(result) || "⛔ I couldn't extract a reply from the model.";
          responseText = truncateForDiscord(responseText);

          const outEmbed = new EmbedBuilder()
            .setTitle(`Gemini • ${selectedModelId || 'flash'}`)
            .setDescription(responseText)
            .setFooter({ text: `Requested by ${interaction.user.tag}` })
            .setTimestamp();

          await interaction.editReply({ embeds: [outEmbed] });
        } catch (err) {
          console.error("Error calling Gemini (prompt):", err);
          // If 404, try rotating models and retry once
          const status = err?.status || err?.statusCode || (err?.response && err.response.status);
          if (status === 404) {
            console.warn("Received 404 from model. Re-initializing model candidates and retrying...");
            await initFlashModel();
            if (flashModel) {
              try {
                const retryRes = await flashModel.generateContent(userPrompt);
                let retryText = extractTextFromAIResult(retryRes) || "⛔ No reply on retry.";
                retryText = truncateForDiscord(retryText);
                await interaction.editReply({ content: retryText });
                return;
              } catch (e2) {
                console.error("Retry also failed:", e2);
              }
            }
          }
          try { await interaction.editReply("❌ Failed to get a response from Gemini. Try again later."); } catch {}
        }
      }

      return;
    }

    // Buttons
    if (interaction.isButton && interaction.isButton()) {
      const id = interaction.customId;

      if (id === 'gemini_flash') {
        const channel = interaction.channel;
        if (!channel || !interaction.guild) return interaction.reply({ content: "Can't create a thread here.", ephemeral: true });

        try {
          const thread = await channel.threads.create({
            name: `gemini-flash-${interaction.user.username}`.slice(0, 100),
            type: ChannelType.PublicThread,
            autoArchiveDuration: 60
          });

          activeThreads.set(thread.id, "flash");

          const starterEmbed = new EmbedBuilder()
            .setTitle("Gemini • Flash Thread")
            .setDescription("💬 Welcome! This thread is linked to the Gemini model. Type your prompts here and the bot will reply.")
            .addFields({ name: "Tip", value: "Ask short, clear prompts for best results." })
            .setFooter({ text: `Thread created by ${interaction.user.tag}` })
            .setTimestamp();

          await thread.send({ content: `Hello <@${interaction.user.id}> — I'll respond to prompts you post here using ${selectedModelId || 'the configured model'}.`, embeds: [starterEmbed] });

          await interaction.reply({
            content: `🧵 Thread created: <#${thread.id}> — I'll respond in this thread.`,
            ephemeral: true
          });
        } catch (err) {
          console.error("Failed to create thread:", err);
          try { await interaction.reply({ content: "❌ Failed to create a thread here.", ephemeral: true }); } catch {}
        }

        return;
      }

      if (interaction.customId === 'gemini_pro') {
        return interaction.reply({ content: "Gemini Pro isn't available yet — stay tuned!", ephemeral: true });
      }
    }
  } catch (err) {
    console.error("Error handling interaction:", err);
    try {
      if (!interaction.replied && !interaction.deferred) {
        await interaction.reply({ content: "❌ An internal error occurred handling your interaction.", ephemeral: true });
      }
    } catch {}
  }
});

/* ===========================
   Message create (Anna auto-reply + thread AI)
=========================== */
client.on('messageCreate', async (message) => {
  try {
    if (message.author?.bot) return;
    if (!message.guild) return;

    // Anna auto-reply
    const guildActivated = activatedGuilds.has(message.guild.id);
    if (guildActivated && /anna/i.test(message.content)) {
      try {
        await message.channel.sendTyping();
        await new Promise(r => setTimeout(r, 1200));
        await message.reply({ content: `👋 You mentioned Anna!\n> ${message.content}`, allowedMentions: { repliedUser: true } });
      } catch (err) {
        console.error("Failed to send Anna auto-reply:", err);
      }
    }

    // Thread-based Gemini replies
    const channelId = message.channel.id;
    if (activeThreads.has(channelId)) {
      const model = activeThreads.get(channelId);
      const userPrompt = message.content?.trim();
      if (!userPrompt) return;
      if (userPrompt.startsWith('/')) return;

      if (model === 'flash') {
        if (!flashModel) {
          // Try to re-init once
          await initFlashModel();
          if (!flashModel) {
            try { await message.reply("❌ Gemini not initialized. Ask the admin to set GEMINI_API_KEY and verify models."); } catch {}
            return;
          }
        }

        try {
          await message.channel.sendTyping();
          const result = await flashModel.generateContent(userPrompt);
          let responseText = extractTextFromAIResult(result) || "⛔ I couldn't extract a reply from the model.";
          responseText = truncateForDiscord(responseText);
          await message.reply(responseText);
        } catch (err) {
          console.error("Error calling Gemini (thread):", err);
          const status = err?.status || err?.statusCode || (err?.response && err.response.status);
          if (status === 404) {
            // rotate models and try again once
            console.warn("404 from model during thread reply; re-initializing candidate list...");
            await initFlashModel();
            if (flashModel) {
              try {
                const retry = await flashModel.generateContent(userPrompt);
                const retryText = truncateForDiscord(extractTextFromAIResult(retry) || "⛔ No reply on retry.");
                await message.reply(retryText);
                return;
              } catch (e2) {
                console.error("Retry after re-init also failed:", e2);
              }
            }
            try { await message.reply("❌ Gemini model returned 404 and couldn't be re-initialized. Admin: check API key and available model IDs."); } catch {}
            return;
          }

          try { await message.reply("❌ Failed to get a response from Gemini. Try again later."); } catch {}
        }
      }
    }
  } catch (err) {
    console.error("Unexpected error in messageCreate:", err);
  }
});

/* ===========================
   Login
=========================== */
client.login(DISCORD_TOKEN)
  .catch(err => {
    console.error("Failed to login:", err);
    process.exit(1);
  });
