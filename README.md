# Meme Launch Manager

This project is an automatic meme coin generation project based on real-time trends in Korea using CrewAi.

It consists of two main agent crews.

1. Trending Scraper: Scrapes the trends that are being discussed in Korea from all Korean trending services and determines the most discussed keywords by AI.

2. Meme Deployer: Taking the trending keywords determined by the Trending Scraper, it creates metadata for meme tokens and utilizes it to deploy meme tokens.

## How to run

Set the API KEY in the .env file

```bash
#LLM
MODEL=
GEMINI_API_KEY=

#tavily
TAVILY_API_KEY=

#cloudflare pages
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=
```

Enter the command below to run it

```bash
crewai flow kickoff
```

Select the desired trending keyword

```bash
📢 Top trending keywords with reasons:

1. 헌드레드 라인 — Related to the game The Hundred Line -Last Defense Academy.
2. 안아랑 — South Korean Instagram influencer and YouTuber.
3. 여우도시 — A server in the game 화양씨, possibly related to GTA.
4. 보스로라 — A Pokemon.
5. 에제 — Eberechi Eze, an English footballer.

Choose the trend keyword number you want. (default=1):
```

Common metadata output (수정예정)

````bash
=== Final Meme Token Metadata (pre-website) ===

{'raw': '```json\n{\n  "name": "Anarang Coin",\n  "symbol": "ARANG",\n  "description": "The official token of the Anarang fan club! Hodl to show your love for the queen of K-beauty and comfy streams. Get ready for exclusive content and maybe, just maybe, a virtual hug! 💖"\n}\n```'}
````

You can make token website

```bash
Do you want to create and deploy a website? (default=n):
```

Token website URL (수정예정)

```bash
🖼 Copied token_image.png → output/site/images
🚀 Starting deployment via Cloudflare Pages (Wrangler Direct Upload, single project)...

📦 Project name: site-site
📁 Deploy directory: output/site
✅ Pages project 'site-site' already exists.
🚚 Uploading files via Wrangler...
✅ Deployed output/site → https://example.site-site-example.pages.dev

📝 JSON report saved to `output/deployment.json`
```

# Project Details

## Trending Scraper

## Meme Deployer
