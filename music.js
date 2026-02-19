import { createRequire } from "module";
const require = createRequire(import.meta.url);
const { Manager } = require("magmastream");

import dotenv from "dotenv";
dotenv.config();

import { Client, GatewayIntentBits, ActivityType, REST, Routes, SlashCommandBuilder } from "discord.js";

const TOKEN = process.env.DISCORD_TOKEN;
if (!TOKEN) {
  console.error("Missing DISCORD_TOKEN in .env");
  process.exit(1);
}

const LAVALINK_HOST = process.env.LAVALINK_HOST || "localhost";
const LAVALINK_PORT = parseInt(process.env.LAVALINK_PORT || "2333", 10);
const LAVALINK_PASSWORD = process.env.LAVALINK_PASSWORD || "youshallnotpass";
const LAVALINK_SECURE = (process.env.LAVALINK_SECURE === "true") || (LAVALINK_PORT === 443);

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

const manager = new Manager({
  nodes: [
    {
      identifier: "lava-node-1",
      host: LAVALINK_HOST,
      port: LAVALINK_PORT,
      password: LAVALINK_PASSWORD,
      secure: LAVALINK_SECURE,
      retryAmount: 5,
      retryDelay: 5000,
      userId: "1360329809670045731"
    }
  ],
  send: (id, payload) => {
    const guild = client.guilds.cache.get(id);
    if (guild) guild.shard.send(payload);
  },
  autoPlay: true,
  plugins: [],
  clientName: "AnnaMusic",
  playNextOnEnd: true,
  userId: "1360329809670045731"
});

client.once("clientReady", async () => {
  console.log(`Logged in as ${client.user.tag} (${client.user.id})`);

  client.user.setPresence({
    status: "dnd",
    activities: [{ name: "/play", type: ActivityType.Playing }]
  });

  manager.init("1360329809670045731");

  const commands = [
    new SlashCommandBuilder()
      .setName("play")
      .setDescription("Play a song (search or URL)")
      .addStringOption(opt => opt.setName("query").setDescription("Song name or URL").setRequired(true)),
    new SlashCommandBuilder()
      .setName("stop")
      .setDescription("Stop playback and leave"),
    new SlashCommandBuilder()
      .setName("loop")
      .setDescription("Toggle loop for current queue"),
    new SlashCommandBuilder()
      .setName("volume")
      .setDescription("Set player volume 0-100")
      .addIntegerOption(opt => opt.setName("amount").setDescription("0-100").setRequired(true))
  ].map(c => c.toJSON());

  const rest = new REST({ version: "10" }).setToken(TOKEN);
  try {
    const clientId = client.user.id;
    await rest.put(Routes.applicationCommands(clientId), { body: commands });
    console.log("Slash commands registered.");
  } catch (err) {
    console.error("Failed to register commands:", err);
  }
});

manager.on("nodeConnect", node => console.log(`Lavalink node "${node.options.identifier}" connected.`));
manager.on("nodeError", (node, error) => console.error(`Node ${node.options.identifier} error:`, error));

manager.on("trackStart", (player, track) => {
  try {
    const textChannel = client.channels.cache.get(player.textChannel);
    if (textChannel && textChannel.isTextBased()) {
      textChannel.send(`🎵 Now playing: **${track.title}**`);
    }
  } catch (e) { console.warn("Could not send trackStart msg:", e); }
});

manager.on("queueEnd", player => {
  setTimeout(() => {
    if (!player.playing && !player.paused) {
      try { player.destroy(); } catch (e) { /* ignore */ }
    }
  }, 2500);
});

client.on("raw", d => manager.updateVoiceState(d));

client.on("interactionCreate", async (interaction) => {
  if (!interaction.isChatInputCommand()) return;
  const { commandName, guild, member } = interaction;
  if (!guild) return interaction.reply({ content: "This command must be used in a server.", ephemeral: true });

  const voiceChannel = member?.voice?.channel;
  if (commandName === "play") {
    const query = interaction.options.getString("query");

    if (!voiceChannel) return interaction.reply({ content: "Join a voice channel first.", ephemeral: true });

    let player = manager.players.get(guild.id);
    if (!player) {
      player = manager.create({
        guild: guild.id,
        voiceChannel: voiceChannel.id,
        textChannel: interaction.channelId,
        selfDeafen: true
      });
      player.connect();
    } else if (player.voiceChannel !== voiceChannel.id) {
      try { await player.setVoiceChannel(voiceChannel.id); } catch (err) { /* ignore */ }
    }

    await interaction.deferReply();

    const res = await manager.search(query, interaction.user);
    if (!res || res.loadType === "NO_MATCHES") {
      return interaction.followUp({ content: "No results found.", ephemeral: true });
    }
    if (res.loadType === "LOAD_FAILED") {
      return interaction.followUp({ content: "Search/load failed.", ephemeral: true });
    }

    if (res.loadType === "PLAYLIST_LOADED") {
      player.queue.add(res.tracks);
      if (!player.playing && !player.paused) player.play();
      return interaction.followUp(`✅ Playlist added (${res.tracks.length} tracks).`);
    }

    const track = res.tracks[0];
    player.queue.add(track);
    if (!player.playing && !player.paused) player.play();
    return interaction.followUp(`🎵 Added to queue: **${track.title}**`);
  }

  if (commandName === "stop") {
    const player = manager.players.get(guild.id);
    if (!player) return interaction.reply({ content: "Nothing is playing.", ephemeral: true });
    player.destroy();
    return interaction.reply("⏹️ Stopped and left voice.");
  }

  if (commandName === "loop") {
    const player = manager.players.get(guild.id);
    if (!player) return interaction.reply({ content: "Nothing is playing.", ephemeral: true });
    player.setQueueRepeat(!player.queueRepeat);
    return interaction.reply(`🔁 Loop: **${player.queueRepeat ? "Enabled" : "Disabled"}**`);
  }

  if (commandName === "volume") {
    const amount = interaction.options.getInteger("amount");
    if (amount < 0 || amount > 100) return interaction.reply({ content: "Volume must be 0-100.", ephemeral: true });
    const player = manager.players.get(guild.id);
    if (!player) return interaction.reply({ content: "Nothing is playing.", ephemeral: true });
    player.setVolume(amount);
    return interaction.reply(`🔊 Volume set to **${amount}%**`);
  }
});

client.login(TOKEN);
