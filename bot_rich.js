const RPC = require("discord-rpc");

const clientId = "1360329809670045731";

const rpc = new RPC.Client({ transport: "ipc" });

rpc.on("ready", () => {
  console.log("Connected to Discord");

  rpc.setActivity({
    state: "Playing Bot Coding",
    details: "Visual Studio",
    startTimestamp: new Date(),
    partySize: 2,
    partyMax: 2,
    instance: false,
  });
});

rpc.login({ clientId }).catch(err => {
  console.error("Login failed:", err);
});
