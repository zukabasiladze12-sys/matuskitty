# Sarcastic Discord Bot

A Discord bot powered by Google Gemini that roasts your friends and answers with attitude.

## Features

- **@ the bot** — it'll respond with sass, using recent channel messages for context
- `!roast @user` — custom roast for someone
- `!ship @user1 @user2` — chaotic compatibility analysis
- `!8ball <question>` — sarcastic magic 8 ball

## Setup

### 1. Get your tokens

**Discord Bot Token:**
1. Go to https://discord.com/developers/applications
2. Click **New Application** → name it
3. Left sidebar → **Bot** → **Reset Token** → copy it
4. On the same Bot page, scroll down and turn ON **Message Content Intent**
5. Left sidebar → **OAuth2** → **URL Generator**
   - Scopes: `bot`, `applications.commands`
   - Bot Permissions: `Send Messages`, `Read Message History`, `View Channels`
6. Open the generated URL in your browser → invite the bot to your server

**Gemini API Key:**
1. Go to https://aistudio.google.com/app/apikey
2. Create API key (free)
3. Copy it

### 2. Run locally

```bash
pip install -r requirements.txt
```

Make a copy of `.env.example` and rename it to `.env`. Fill in your tokens:

```
DISCORD_TOKEN=your_discord_token
GEMINI_API_KEY=your_gemini_key
```

Run it:

```bash
python bot.py
```

### 3. Deploy to Railway (24/7 hosting)

1. Push this folder to a GitHub repo (the `.gitignore` makes sure your `.env` doesn't get pushed)
2. Go to https://railway.app → **New Project** → **Deploy from GitHub repo**
3. Pick your repo
4. In Railway dashboard → **Variables** tab → add:
   - `DISCORD_TOKEN` = your token
   - `GEMINI_API_KEY` = your key
5. Done. Bot runs 24/7.

## Customizing

Open `bot.py` and edit the `SYSTEM_PROMPT` to change the bot's personality. Add new commands by following the pattern of `!roast` or `!ship`.

## Cost

Gemini's free tier is generous — a small friend-group bot won't hit the limits.
