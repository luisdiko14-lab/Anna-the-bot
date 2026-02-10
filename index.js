const express = require("express");
const path = require("path");

const app = express();

// Replit exposes port 80 externally and forwards it to this port
const PORT = 3000;

// serve static files
app.use(express.static(path.join(__dirname, "public")));

app.get("/", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 App running on internal port ${PORT} (external :80 via Replit)`);
});
