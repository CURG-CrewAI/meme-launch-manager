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

#serper
SERPER_API_KEY=

#cloudflare pages
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ACCOUNT_ID=
```

Enter the command below to run it
* Before you run it, you must install wrangler
  ```
  $ npm install -g wrangler
  ```

```bash
crewai flow kickoff
```

Select the desired trending keyword

```bash
📢 Top trending keywords with reasons:

1. 이대호 — Appearing on 'Same Bed, Different Dreams 2' with his family.
2. 김병만 — Getting remarried and revealing his wife on 'Joseon's Lover'.
3. 트럼프 — Claimed a 'purge or revolution' is happening in South Korea.
4. 노란봉투법 — Ruling party pushing its passage, limiting damage claims against striking workers.
5. 고든 창 — Supported Trump's statement and criticized President Lee as anti-American.

Choose the trend keyword number you want. (default=1):
```

You can see a metadata in CLI and check metadata.json

```bash
# CLI
=== Basic Meme Token Metadata ===

{
    "name": "The Art of the Deal Token",
    "symbol": "$TRUMPCARD",
    "description": "In a world drowning in 'fake news' and 'witch hunts,' only one token dares to be truly, unequivocally, fantastically... YUGE! Introducing The Art of the Deal Token ($TRUMPCARD), the revolutionary new memecoin built on the undeniable power of, well, *him*. Forget fundamentals, whitepapers, or even basic economics – this coin runs on pure, unadulterated, glorious *vibrations*. From the bustling chat rooms of Korean crypto-bros (who are *very* interested in global political drama, especially when it's this spicy) predicting election outcomes to global headlines swinging wildly with every tweet (or Truth Social post), $TRUMPCARD captures the essence of an era where volatility is the new stability. We're not just making America great again, we're making *memecoins* great again, one outrageous headline at a time. It's truly a 'beautiful' coin, folks, the most beautiful.",
    "features": [
        "Executive Order Governance ($EOG) Protocol: Holders can vote on \"policy changes\" like whether the next pump will be \"bigger than anyone has ever seen\" or if a certain chart pattern is \"rigged.\" Decisions are final, indisputable, and often change without notice.",
        "Rally Reflexivity Mechanism: Price action directly correlates to the volume of cable news mentions and social media engagement. The louder the noise, the higher the highs, and the lower the... well, let's not talk about the low points. They're \"fake news.\"",
        "Gold Standard Backing (Figuratively): Our tokenomics are inspired by the sheer perceived value of gold-plated everything. While not actually backed by gold, it promises a future where everything feels \"golden,\" even your portfolio losses.",
        "Truth Social Integration (Conceptual): Any major announcement, rebuttal, or rhetorical flourish on Truth Social (or any platform he's allowed on next week) directly fuels the token's 'Make It Go Up' mechanism. Positive sentiment, real or imagined, is algorithmically factored in."
    ],
    "warning": "Look, folks, some people are saying this token is going to the moon, others are saying it's a 'disaster.' Both are probably true, depending on the news cycle. This isn't financial advice; it's *performance art* in its most glorious, slightly chaotic form. If you're looking for stability, go watch paint dry. If you're looking for excitement and the chance to buy low (or high, depends on who you ask), then $TRUMPCARD is your huckleberry. Remember, we don't do 'losing' here; we just have 'temporary setbacks' and 'unprecedented comebacks.' Investing in $TRUMPCARD means you're investing in the *narrative*. And what a narrative it is! Do your own research, but really, just trust us. It's gonna be huge.",
    "hashtags": [
        "#TRUMPCARD",
        "#MAGAFI",
        "#Memecoin",
        "#CryptoPolitics",
        "#YugeReturns",
        "#TheDonaldCoin",
        "#HypeIsReal"
    ]
}
```

```
//===output/metadata.json===//
{
  "name": "The Art of the Deal Token",
  "symbol": "$TRUMPCARD",
  "description": "In a world drowning in 'fake news' and 'witch hunts,' only one token dares to be truly, unequivocally, fantastically... YUGE! Introducing The Art of the Deal Token ($TRUMPCARD), the revolutionary new memecoin built on the undeniable power of, well, *him*. Forget fundamentals, whitepapers, or even basic economics – this coin runs on pure, unadulterated, glorious *vibrations*. From the bustling chat rooms of Korean crypto-bros (who are *very* interested in global political drama, especially when it's this spicy) predicting election outcomes to global headlines swinging wildly with every tweet (or Truth Social post), $TRUMPCARD captures the essence of an era where volatility is the new stability. We're not just making America great again, we're making *memecoins* great again, one outrageous headline at a time. It's truly a 'beautiful' coin, folks, the most beautiful.",
  "features": [
    "Executive Order Governance ($EOG) Protocol: Holders can vote on \"policy changes\" like whether the next pump will be \"bigger than anyone has ever seen\" or if a certain chart pattern is \"rigged.\" Decisions are final, indisputable, and often change without notice.",
    "Rally Reflexivity Mechanism: Price action directly correlates to the volume of cable news mentions and social media engagement. The louder the noise, the higher the highs, and the lower the... well, let's not talk about the low points. They're \"fake news.\"",
    "Gold Standard Backing (Figuratively): Our tokenomics are inspired by the sheer perceived value of gold-plated everything. While not actually backed by gold, it promises a future where everything feels \"golden,\" even your portfolio losses.",    "Truth Social Integration (Conceptual): Any major announcement, rebuttal, or rhetorical flourish on Truth Social (or any platform he's allowed on next week) directly fuels the token's 'Make It Go Up' mechanism. Positive sentiment, real or imagined, is algorithmically factored in."
  ],
  "warning": "Look, folks, some people are saying this token is going to the moon, others are saying it's a 'disaster.' Both are probably true, depending on the news cycle. This isn't financial advice; it's *performance art* in its most glorious, slightly chaotic form. If you're looking for stability, go watch paint dry. If you're looking for excitement and the chance to buy low (or high, depends on who you ask), then $TRUMPCARD is your huckleberry. Remember, we don't do 'losing' here; we just have 'temporary setbacks' and 'unprecedented comebacks.' Investing in $TRUMPCARD means you're investing in the *narrative*. And what a narrative it is! Do your own research, but really, just trust us. It's gonna be huge.",
  "hashtags": [
    "#TRUMPCARD",
    "#MAGAFI",
    "#Memecoin",
    "#CryptoPolitics",
    "#YugeReturns",
    "#TheDonaldCoin",
    "#HypeIsReal"
  ]
}
```

You can make memetoken website

```bash
Do you want to create and deploy a website? (default=n):
```

You can get a memetoken website url and add web url to your metadata.json

```bash
🖼 Copied token_image.png → output/site/images
🚀 Starting deployment via Cloudflare Pages (Wrangler Direct Upload, single project)...

📦 Project name: site-site
📁 Deploy directory: output/site
✅ Pages project 'site-site' already exists.
🚚 Uploading files via Wrangler...
✅ Deployed output/site → https://aaa.site-site-aaa.pages.dev

📝 JSON report saved to `output/deployment.json`
✅ output/metadata.json에 'Website: https://aaa.site-site-aaa.pages.dev' 추가 완료.

=== Advanced Meme Token Metadata ===

{
    "name": "The Art of the Deal Token",
    "symbol": "$TRUMPCARD",
    "description": "In a world drowning in 'fake news' and 'witch hunts,' only one token dares to be truly, unequivocally, fantastically... YUGE! Introducing The Art of the Deal Token ($TRUMPCARD), the revolutionary new memecoin built on the undeniable power of, well, *him*. Forget fundamentals, whitepapers, or even basic economics – this coin runs on pure, unadulterated, glorious *vibrations*. From the bustling chat rooms of Korean crypto-bros (who are *very* interested in global political drama, especially when it's this spicy) predicting election outcomes to global headlines swinging wildly with every tweet (or Truth Social post), $TRUMPCARD captures the essence of an era where volatility is the new stability. We're not just making America great again, we're making *memecoins* great again, one outrageous headline at a time. It's truly a 'beautiful' coin, folks, the most beautiful.",
    "features": [
        "Executive Order Governance ($EOG) Protocol: Holders can vote on \"policy changes\" like whether the next pump will be \"bigger than anyone has ever seen\" or if a certain chart pattern is \"rigged.\" Decisions are final, indisputable, and often change without notice.",
        "Rally Reflexivity Mechanism: Price action directly correlates to the volume of cable news mentions and social media engagement. The louder the noise, the higher the highs, and the lower the... well, let's not talk about the low points. They're \"fake news.\"",
        "Gold Standard Backing (Figuratively): Our tokenomics are inspired by the sheer perceived value of gold-plated everything. While not actually backed by gold, it promises a future where everything feels \"golden,\" even your portfolio losses.",
        "Truth Social Integration (Conceptual): Any major announcement, rebuttal, or rhetorical flourish on Truth Social (or any platform he's allowed on next week) directly fuels the token's 'Make It Go Up' mechanism. Positive sentiment, real or imagined, is algorithmically factored in."
    ],
    "warning": "Look, folks, some people are saying this token is going to the moon, others are saying it's a 'disaster.' Both are probably true, depending on the news cycle. This isn't financial advice; it's *performance art* in its most glorious, slightly chaotic form. If you're looking for stability, go watch paint dry. If you're looking for excitement and the chance to buy low (or high, depends on who you ask), then $TRUMPCARD is your huckleberry. Remember, we don't do 'losing' here; we just have 'temporary setbacks' and 'unprecedented comebacks.' Investing in $TRUMPCARD means you're investing in the *narrative*. And what a narrative it is! Do your own research, but really, just trust us. It's gonna be huge.",
    "hashtags": [
        "#TRUMPCARD",
        "#MAGAFI",
        "#Memecoin",
        "#CryptoPolitics",
        "#YugeReturns",
        "#TheDonaldCoin",
        "#HypeIsReal"
    ],
    "Website": "https://aaa.site-site-aaa.pages.dev"
}
```

```
//===output/metadata.json===//
{
 {
    "name": "The Art of the Deal Token",
    "symbol": "$TRUMPCARD",
    "description": "In a world drowning in 'fake news' and 'witch hunts,' only one token dares to be truly, unequivocally, fantastically... YUGE! Introducing The Art of the Deal Token ($TRUMPCARD), the revolutionary new memecoin built on the undeniable power of, well, *him*. Forget fundamentals, whitepapers, or even basic economics – this coin runs on pure, unadulterated, glorious *vibrations*. From the bustling chat rooms of Korean crypto-bros (who are *very* interested in global political drama, especially when it's this spicy) predicting election outcomes to global headlines swinging wildly with every tweet (or Truth Social post), $TRUMPCARD captures the essence of an era where volatility is the new stability. We're not just making America great again, we're making *memecoins* great again, one outrageous headline at a time. It's truly a 'beautiful' coin, folks, the most beautiful.",
    "features": [
        "Executive Order Governance ($EOG) Protocol: Holders can vote on \"policy changes\" like whether the next pump will be \"bigger than anyone has ever seen\" or if a certain chart pattern is \"rigged.\" Decisions are final, indisputable, and often change without notice.",
        "Rally Reflexivity Mechanism: Price action directly correlates to the volume of cable news mentions and social media engagement. The louder the noise, the higher the highs, and the lower the... well, let's not talk about the low points. They're \"fake news.\"",
        "Gold Standard Backing (Figuratively): Our tokenomics are inspired by the sheer perceived value of gold-plated everything. While not actually backed by gold, it promises a future where everything feels \"golden,\" even your portfolio losses.",
        "Truth Social Integration (Conceptual): Any major announcement, rebuttal, or rhetorical flourish on Truth Social (or any platform he's allowed on next week) directly fuels the token's 'Make It Go Up' mechanism. Positive sentiment, real or imagined, is algorithmically factored in."
    ],
    "warning": "Look, folks, some people are saying this token is going to the moon, others are saying it's a 'disaster.' Both are probably true, depending on the news cycle. This isn't financial advice; it's *performance art* in its most glorious, slightly chaotic form. If you're looking for stability, go watch paint dry. If you're looking for excitement and the chance to buy low (or high, depends on who you ask), then $TRUMPCARD is your huckleberry. Remember, we don't do 'losing' here; we just have 'temporary setbacks' and 'unprecedented comebacks.' Investing in $TRUMPCARD means you're investing in the *narrative*. And what a narrative it is! Do your own research, but really, just trust us. It's gonna be huge.",
    "hashtags": [
        "#TRUMPCARD",
        "#MAGAFI",
        "#Memecoin",
        "#CryptoPolitics",
        "#YugeReturns",
        "#TheDonaldCoin",
        "#HypeIsReal"
    ],
+   "Website": "https://aaa.site-site-aaa.pages.dev"
}
```

# Project Details

## Trending Scraper

## Meme Deployer
