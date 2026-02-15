// index.js (ES module)
import dotenv from 'dotenv';
dotenv.config();

import {
  Client,
  GatewayIntentBits,
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  ChannelType,
  SlashCommandBuilder,
} from 'discord.js';

import { REST } from '@discordjs/rest';
import { Routes } from 'discord-api-types/v10';

import { GoogleGenerativeAI } from '@google/generative-ai';

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

/* ===========================
   Google Gemini / Generative AI
   (initialize with your GEMINI_API_KEY env var)
   Example SDK usage: getGenerativeModel + generateContent.
=========================== */
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const flashModel = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

/* State */
const activatedGuilds = new Set();   // guild IDs where Anna auto-response is enabled
const activeThreads = new Map();     // threadId -> modelType ('flash', ...)

/* ===========================
   REGISTER SLASH COMMANDS
=========================== */
const commands = [
  new SlashCommandBuilder()
    .setName('activate')
    .setDescription('Activate Anna auto-response'),

  new SlashCommandBuilder()
    .setName('startconversation')
    .setDescription('Start a Gemini conversation')
].map(cmd => cmd.toJSON());

const registerCommands = async () => {
  const rest = new REST({ version: '10' }).setToken(process.env.DISCORD_TOKEN);
  const clientId = process.env.CLIENT_ID || client.user.id;
  
  try {
    console.log("Started refreshing application (/) commands.");
    await rest.put(
      Routes.applicationCommands(clientId),
      { body: commands }
    );
    console.log("Successfully reloaded application (/) commands.");
  } catch (err) {
    console.error("Failed to register slash commands:", err);
  }
};

/* ===========================
   READY
   =========================== */
client.once('ready', () => {
  console.log(`Logged in as ${client.user.tag}`);
  registerCommands();
});

/* ===========================
   INTERACTION HANDLER (slash & buttons)
   =========================== */
client.on('interactionCreate', async (interaction) => {
  try {
    if (interaction.isChatInputCommand()) {
      if (interaction.commandName === 'activate') {
        if (!interaction.guild) {
          return interaction.reply({ content: "This command must be used in a server (guild).", ephemeral: true });
        }
        activatedGuilds.add(interaction.guild.id);
        return interaction.reply({
          content: "✅ Activation enabled. I will respond when a message contains **Anna** in this server.",
          ephemeral: true
        });
      }

      if (interaction.commandName === 'startconversation') {
        const row = new ActionRowBuilder().addComponents(
          new ButtonBuilder()
            .setCustomId('gemini_flash')
            .setLabel('Gemini Flash')
            .setStyle(ButtonStyle.Primary),

          new ButtonBuilder()
            .setCustomId('gemini_pro')
            .setLabel('Gemini Pro')
            .setStyle(ButtonStyle.Secondary)
            .setDisabled(true)
        );

        return interaction.reply({
          content: "Choose a Gemini model:",
          components: [row],
          ephemeral: true
        });
      }
    }

    if (interaction.isButton()) {
      if (interaction.customId === 'gemini_flash') {
        if (!interaction.channel || !interaction.guild) {
          return interaction.reply({ content: "Can't create a thread here.", ephemeral: true });
        }

        const thread = await interaction.channel.threads.create({
          name: `Gemini-Flash-${interaction.user.username}`,
          type: ChannelType.PublicThread,
          autoArchiveDuration: 60
        });

        activeThreads.set(thread.id, "flash");

        return interaction.reply({
          content: `🧵 Thread created: <#${thread.id}> — I'll respond in this thread.`,
          ephemeral: true
        });
      }
    }
  } catch (err) {
    console.error("Error handling interaction:", err);
    if (!interaction.replied && !interaction.deferred) {
      try { await interaction.reply({ content: "❌ An error occurred.", ephemeral: true }); } catch {}
    }
  }
});

/* ===========================
   MESSAGE CREATE
   =========================== */
client.on('messageCreate', async (message) => {
  if (message.author.bot) return;
  if (!message.guild) return;

  const guildActivated = activatedGuilds.has(message.guild.id);

  if (guildActivated && message.content.toLowerCase().includes("anna")) {
    try {
      await message.channel.sendTyping();
      await new Promise(resolve => setTimeout(resolve, 1500));
      await message.reply(`👋 You mentioned Anna!\nMessage: "${message.content}"`);
    } catch (err) {
      console.error("Failed to send Anna auto-reply:", err);
    }
  }

  if (activeThreads.has(message.channel.id)) {
    const modelType = activeThreads.get(message.channel.id);
    const userPrompt = message.content?.trim();
    if (!userPrompt) return;

    if (modelType === "flash") {
      try {
        const result = await flashModel.generateContent(userPrompt);
        let responseText = null;
        if (result?.response && typeof result.response.text === 'function') {
          responseText = result.response.text();
        } else if (result?.response?.text) {
          responseText = result.response.text;
        } else if (typeof result === 'string') {
          responseText = result;
        } else {
          responseText = "⛔ I couldn't extract a reply from the model.";
        }

        const maxLen = 1900;
        if (responseText.length > maxLen) {
          responseText = responseText.slice(0, maxLen) + "\n\n...(truncated)";
        }

        await message.reply(responseText);
      } catch (err) {
        console.error("Error calling Gemini model:", err);
        try { await message.reply("❌ Failed to get a response from the AI."); } catch {}
      }
    }
  }
});

/* ===========================
   Login
   =========================== */
client.login(process.env.DISCORD_TOKEN)
  .catch(err => {
    console.error("Failed to login:", err);
    process.exit(1);
  });
