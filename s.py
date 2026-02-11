from PIL import Image, ImageDraw
import requests
from io import BytesIO
import random

# Discord avatar URL
avatar_url = "https://cdn.discordapp.com/avatars/1360329809670045731/905fb8cabac5e21c903897c2a6e98c53.webp?size=128"

# Download avatar
response = requests.get(avatar_url)
avatar = Image.open(BytesIO(response.content)).convert("RGBA")
size = avatar.size

frames = []
num_frames = 12  # number of frames
emoji_count = 12  # number of “emoji” sparkles per frame

for i in range(num_frames):
    frame = Image.new("RGBA", size, (0, 0, 0, 0))
    frame.paste(avatar, (0, 0), avatar)

    draw = ImageDraw.Draw(frame)

    for _ in range(emoji_count):
        x = random.randint(0, size[0]-14)
        y = random.randint(0, size[1]-14)

        # Randomly pick ✅ (green check) or 🌸 (pink flower)
        if random.choice([True, False]):
            # ✅ green check: small green rectangle with white check mark line
            draw.rectangle((x, y, x+8, y+8), fill=(0,200,0,255))
            draw.line((x+2, y+4, x+4, y+6, x+6, y+2), fill=(255,255,255,255), width=1)
        else:
            # 🌸 pink flower: pink circle with 5 small petals
            draw.ellipse((x, y, x+8, y+8), fill=(255,105,180,255))

    frames.append(frame)

# Save animated GIF
frames[0].save(
    "avatar_with_drawn_emojis.gif",
    save_all=True,
    append_images=frames[1:],
    optimize=False,
    duration=150,
    loop=0
)

print("✅ Saved avatar_with_drawn_emojis.gif!")
