// index.js (ES module)
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
  console.warn("Warning: GEMINI_API_KEY not set. AI features will error until you set GEMINI_API_KEY.");
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
   Google Gemini / Generative AI
=========================== */
const genAI = GEMINI_API_KEY ? new GoogleGenerativeAI(GEMINI_API_KEY) : null;
const flashModel = genAI ? genAI.getGenerativeModel({ model: "gemini-1.5-flash-002" }) : null;

/* ===========================
   State
=========================== */
const activatedGuilds = new Set();   // guild IDs where Anna auto-response is enabled
const activeThreads = new Map();     // threadId -> modelType ('flash', ...)

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
    // Registers global application commands - can take up to an hour to propagate.
    await rest.put(Routes.applicationCommands(applicationId), { body: commands });
    console.log("Commands registered.");
  } catch (err) {
    console.error("Failed to register slash commands:", err);
  }
};

/* ===========================
   Utilities
=========================== */
function extractTextFromAIResult(result) {
  // Try several plausible fields (SDKs vary). Keep this robust.
  try {
    if (!result) return null;

    // If API returns object with response.text() function (some wrappers do this)
    if (result.response && typeof result.response.text === 'function') {
      return result.response.text();
    }

    // If response.text is a string
    if (result.response && typeof result.response.text === 'string') {
      return result.response.text;
    }

    // Some SDKs return an outputText or output string
    if (typeof result.outputText === 'string') {
      return result.outputText;
    }

    if (typeof result === 'string') {
      return result;
    }

    // Fallback: try to inspect nested candidates
    if (Array.isArray(result.candidates) && result.candidates[0]) {
      if (typeof result.candidates[0].text === 'string') return result.candidates[0].text;
      if (typeof result.candidates[0].output === 'string') return result.candidates[0].output;
    }

    // If nothing found
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
   Ready
=========================== */
client.once('ready', async () => {
  console.log(`Logged in as ${client.user.tag} (${client.user.id})`);

  // Register commands using CLIENT_ID (from .env) if provided; otherwise use bot user id.
  const applicationId = CLIENT_ID || client.user.id;
  await registerCommands(applicationId);
});

/* ===========================
   Interaction Handler
=========================== */
client.on('interactionCreate', async (interaction) => {
  try {
    // Slash commands
    if (interaction.isChatInputCommand && interaction.isChatInputCommand()) {
      const name = interaction.commandName;

      if (name === 'activate') {
        if (!interaction.guild) {
          return interaction.reply({ content: "This command must be used in a server (guild).", ephemeral: true });
        }
        activatedGuilds.add(interaction.guild.id);
        return interaction.reply({
          content: "✅ Activation enabled — I will respond when someone mentions **Anna** in this server.",
          ephemeral: true
        });
      }

      if (name === 'startconversation') {
        // Build buttons (we won't change them on click — per your request)
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

        // Public reply with buttons (ephemeral true to avoid channel clutter if desired)
        return interaction.reply({
          content: "✨ Choose a model to start a conversation. (Click a button to create a thread for the AI.)",
          components: [row],
          ephemeral: true
        });
      }

      if (name === 'prompt') {
        const userPrompt = interaction.options.getString('message', true).trim();
        if (!userPrompt) {
          return interaction.reply({ content: "Please provide a prompt.", ephemeral: true });
        }

        // Defer (we may take time calling the AI)
        await interaction.deferReply({ ephemeral: false });

        if (!flashModel) {
          await interaction.editReply("❌ Gemini (flash) model not initialized. Set GEMINI_API_KEY in your .env.");
          return;
        }

        try {
          // Send typing to indicate progress (deferred reply shows loading; still useful)
          // Call the model
          const result = await flashModel.generateContent(userPrompt);

          let responseText = extractTextFromAIResult(result) || "⛔ I couldn't extract a reply from the model.";
          responseText = truncateForDiscord(responseText);

          // Nice embed for a cooler look
          const outEmbed = new EmbedBuilder()
            .setTitle("Gemini • Flash")
            .setDescription(responseText)
            .setFooter({ text: `Requested by ${interaction.user.tag}` })
            .setTimestamp();

          await interaction.editReply({ embeds: [outEmbed] });
        } catch (err) {
          console.error("Error calling Gemini (prompt):", err);
          try {
            await interaction.editReply("❌ Failed to get a response from Gemini. Try again later.");
          } catch {}
        }
      }

      return;
    }

    // Buttons
    if (interaction.isButton && interaction.isButton()) {
      const id = interaction.customId;

      // Only handle gemini flash button here — it will create a thread and NOT attempt to call the model directly.
      if (id === 'gemini_flash') {
        // Ensure we have a proper channel and guild
        const channel = interaction.channel;
        if (!channel || !interaction.guild) {
          return interaction.reply({ content: "Can't create a thread here.", ephemeral: true });
        }

        // Create a public thread in the channel (if possible)
        try {
          // Create thread from the channel (threads.create works on TextBased channels)
          const thread = await channel.threads.create({
            name: `gemini-flash-${interaction.user.username}`.slice(0, 100),
            type: ChannelType.PublicThread,
            autoArchiveDuration: 60
          });

          // Store active thread
          activeThreads.set(thread.id, "flash");

          // Send an initial friendly message in the thread
          const starterEmbed = new EmbedBuilder()
            .setTitle("Gemini • Flash Thread")
            .setDescription("💬 Welcome! This thread is now linked to the Gemini-Flash model. Type your prompts here and the bot will reply.")
            .addFields(
              { name: "Hint", value: "Try: `Explain recursion in simple terms` or `Write a short poem about space`" }
            )
            .setFooter({ text: `Thread created by ${interaction.user.tag}` })
            .setTimestamp();

          await thread.send({ content: `Hello <@${interaction.user.id}> — I’ll respond to prompts you post here.`, embeds: [starterEmbed] });

          // Reply ephemerally to the button click so the original message + buttons remain unchanged (per your request)
          await interaction.reply({
            content: `🧵 Thread created: <#${thread.id}> — I'll respond in this thread. (Only you can see this confirmation.)`,
            ephemeral: true
          });
        } catch (err) {
          console.error("Failed to create thread:", err);
          try { await interaction.reply({ content: "❌ Failed to create a thread here.", ephemeral: true }); } catch {}
        }

        return;
      }

      // If other buttons (like gemini_pro) are clicked, just reply ephemeral that it's unavailable
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
   Message Create (thread + Anna auto-reply)
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
        // brief 'thinking' delay to feel more natural
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

      // Only process text prompts (ignore system messages / commands that start with slash)
      if (userPrompt.startsWith('/')) return;

      if (model === 'flash') {
        if (!flashModel) {
          try { await message.reply("❌ Gemini (flash) not initialized on the bot. Ask the admin to set GEMINI_API_KEY."); } catch {}
          return;
        }

        try {
          await message.channel.sendTyping();
          const result = await flashModel.generateContent(userPrompt);

          let responseText = extractTextFromAIResult(result) || "⛔ I couldn't extract a reply from the model.";
          responseText = truncateForDiscord(responseText);

          await message.reply(responseText);
        } catch (err) {
          console.error("Error calling Gemini (thread):", err);
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
