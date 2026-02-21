const { Client, GatewayIntentBits, ActivityType, REST, Routes, SlashCommandBuilder } = require("discord.js");
const { Manager } = require("magmastream");
require("dotenv").config();

const TOKEN = process.env.DISCORD_TOKEN;
const CLIENT_ID = "1360329809670045731"; // Your bot's client ID

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildVoiceStates,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent,
  ],
});

const manager = new Manager({
  nodes: [
    {
      identifier: "lava-node-1",
      host: process.env.LAVALINK_HOST || "localhost",
      port: parseInt(process.env.LAVALINK_PORT || "2333"),
      password: process.env.LAVALINK_PASSWORD || "youshallnotpass",
      secure: process.env.LAVALINK_SECURE === "true",
    },
  ],
  send(id, payload) {
    const guild = client.guilds.cache.get(id);
    if (guild) guild.shard.send(payload);
  },
});

client.once("ready", async () => {
  console.log(`Logged in as ${client.user.tag}`);
  
  // Critical fix: Initialize manager with the bot's ID
  manager.init(client.user.id);
  
  const commands = [
    new SlashCommandBuilder()
      .setName("play")
      .setDescription("Play a song")
      .addStringOption(opt => opt.setName("query").setDescription("Song name or URL").setRequired(true)),
    new SlashCommandBuilder().setName("stop").setDescription("Stop music"),
  ].map(m => m.toJSON());

  const rest = new REST({ version: "10" }).setToken(TOKEN);
  try {
    await rest.put(Routes.applicationCommands(CLIENT_ID), { body: commands });
    console.log("Music slash commands registered.");
  } catch (err) {
    console.error(err);
  }
});

manager.on("nodeConnect", node => console.log(`Node ${node.options.identifier} connected.`));
manager.on("nodeError", (node, error) => console.error(`Node ${node.options.identifier} error:`, error));

client.on("interactionCreate", async interaction => {
  if (!interaction.isChatInputCommand()) return;
  const { commandName, guildId, member, channelId } = interaction;

  if (commandName === "play") {
    const query = interaction.options.getString("query");
    if (!member.voice.channel) return interaction.reply("Join a voice channel!");

    const player = manager.create({
      guild: guildId,
      voiceChannel: member.voice.channel.id,
      textChannel: channelId,
    });

    if (player.state !== "CONNECTED") player.connect();

    const res = await manager.search(query, interaction.user);
    player.queue.add(res.tracks[0]);
    if (!player.playing && !player.paused && !player.queue.size) player.play();
    
    return interaction.reply(`Queued: ${res.tracks[0].title}`);
  }
});

client.on("raw", d => manager.updateVoiceState(d));
client.login(TOKEN);
