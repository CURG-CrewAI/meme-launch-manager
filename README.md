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
```

Enter the command below to run it

```bash
crewai flow kickoff
```

Select the desired trending keyword

```bash
[Trending Keyword]
1. Keyword
2. Keyword
3. Keyword

✅ Select the number of the trend you want:
```

# Project Details

## Trending Scraper

## Meme Deployer
