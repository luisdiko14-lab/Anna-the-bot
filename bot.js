const { 
  Client, 
  GatewayIntentBits, 
  ActivityType 
} = require('discord.js');

const client = new Client({
  intents: [
    GatewayIntentBits.Guilds,
    GatewayIntentBits.GuildMessages,
    GatewayIntentBits.MessageContent
  ]
});

// 🔐 Put your bot token here
const TOKEN = "MTM2MDMyOTgwOTY3MDA0NTczMQ.GLJsTj.DWHaO6L4NFviUTIMPgVHY9jxIH-hvHq8NF4yww";

// ✅ When bot is ready
client.once('ready', () => {
  console.log(`Logged in as ${client.user.tag}`);

  // Set DND status + Watching Zelda
  client.user.setPresence({
    activities: [{
      name: 'Zelda',
      type: ActivityType.Watching
    }],
    status: 'dnd'
  });
});

// ✅ Prefix commands
const prefix = "!";

client.on('messageCreate', async (message) => {
  if (message.author.bot) return;
  if (!message.content.startsWith(prefix)) return;

  const args = message.content.slice(prefix.length).trim().split(/ +/);
  const command = args.shift().toLowerCase();

  // Show typing
  await message.channel.sendTyping();

  // !ping
  if (command === "ping") {
    setTimeout(() => {
      message.reply("🏓 Pong!");
    }, 800);
  }

  // !hello
  if (command === "hello") {
    setTimeout(() => {
      message.reply(`👋 Hello ${message.author.username}!`);
    }, 800);
  }

  // !avatar
  if (command === "avatar") {
    setTimeout(() => {
      message.reply(message.author.displayAvatarURL({ size: 1024 }));
    }, 800);
  }
});

client.login(TOKEN);
