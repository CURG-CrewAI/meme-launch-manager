# Meme Launch Manager

This project is an automatic meme coin generation project based on real-time trends in Korea using CrewAi.

It consists of two main agent crews.

1. Trending Scraper: Scrapes the trends that are being discussed in Korea from all Korean trending services and determines the most discussed keywords by AI.

2. Meme Deployer: Taking the trending keywords determined by the Trending Scraper, it creates metadata for meme tokens and utilizes it to deploy meme tokens.

## How to run

Set the API KEY in the .env file

```bash
#LLM
# MODEL=gemini/gemini-2.0-flash-001
GEMINI_API_KEY=
OPENAI_API_KEY=

#serper
SERPER_API_KEY=

#cloudflare pages
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=

#telegram
TELEGRAM_BOT_TOKEN=

#r2
R2_ENDPOINT=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET=
CUSTOM_DOMAIN=
WORKER_URL=
```

Enter the command below to run it

```bash
python -m app.bot_entry
```

You can run it in TELEGRAM!!

```bash
"Meme Launch Manager Commands:\n\n"
"/start - Start bot\n"
"/launch - Start meme launch manager\n"
"/cancel - End meme launch manager\n"
"/help - Show help\n"
```
