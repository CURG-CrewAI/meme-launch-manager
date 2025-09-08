#!/usr/bin/env python
from __future__ import annotations

from pydantic import BaseModel, Field
from crewai.flow import Flow, listen, or_, persist, router, start
from utils.metadata_helper import update_metadata

from meme_launch_manager.crews.trending_scraper.trending_scraper import (
    TrendingScraperCrew,
)
from meme_launch_manager.crews.meme_data_generator.meme_data_generator import (
    MemeDataGeneratorCrew,
)
from meme_launch_manager.crews.website_developer.website_developer import (
    WebsiteDeveloper,
)

from utils.metadata_helper import print_metadata
from utils.cli import (
    print_trends,
    prompt_choice_trend,
    prompt_make_site,
    prompt_telegram_url,
    prompt_x_url,
)


class MemeLaunchFlowState(BaseModel):
    top_trends: dict | None = None
    selected_trend: dict | None = None
    token_metadata: dict | None = None
    website_flag: bool = False
    website_url: str | None = None


class MemeLaunchFlow(Flow[MemeLaunchFlowState]):
    @start()
    def run_trending_scraper(self):
        print("👀 Looking for trends in South Korea...")
        top_trends = TrendingScraperCrew().crew().kickoff()
        print_trends(top_trends["trendsWithWhy"])
        self.state.top_trends = top_trends

    @listen(run_trending_scraper)
    def select_trend(self):
        top_trends = self.state.top_trends["trendsWithWhy"]
        self.state.selected_trend = prompt_choice_trend(top_trends, 1)

    @listen(select_trend)
    def run_meme_data_generator(self):
        selected_trend = self.state.selected_trend
        token_metadata = MemeDataGeneratorCrew().crew().kickoff(inputs=selected_trend)
        self.state.token_metadata = token_metadata

    @router(run_meme_data_generator)
    def ask_make_website(self):
        self.state.website_flag = prompt_make_site("n")
        if self.state.website_flag:
            return "Generated"
        else:
            return "Not Generated"

    @listen("Generated")
    def run_website_developer(self):
        token_metadata = self.state.token_metadata["memeTokenMetaData"]
        self.state.website_url = (
            WebsiteDeveloper().crew().kickoff(inputs={"token_metadata": token_metadata})
        )

    @listen(run_website_developer)
    def update_website_url_metadata(self):
        url = self.state.website_url
        update_metadata("output/metadata.json", "WebUrl", url)

    @listen(or_(update_website_url_metadata, "Not Generated"))
    def update_telegram_url_metadata(self):
        url = prompt_telegram_url()
        if url:
            update_metadata("output/metadata.json", "telegramUrl", url)

    @listen(update_telegram_url_metadata)
    def update_x_url_metadata(self):
        url = prompt_x_url()
        if url:
            update_metadata("output/metadata.json", "xUrl", url)

    @listen(update_x_url_metadata)
    def finalize(self):
        print("\n===🎉🎉🎉 Your MemeToken Metadata 🎉🎉🎉===\n")
        print_metadata("output/metadata.json")


def kickoff():
    flow = MemeLaunchFlow()
    flow.kickoff()


def plot():
    flow = MemeLaunchFlow()
    flow.plot()


def test():
    flow = MemeLaunchFlow()
    # 회상 슬픔
    flow.state.token_metadata = {
        "memeTokenMetaData": {
            "name": "LibraryCoin $DAEDO",
            "symbol": "$DAEDO",
            "description": "This meme token eternally honors the first-generation internet broadcaster Daedoseo and celebrates his broadcasting philosophy. The DAEDO token supports online communities that value creativity, communication, and enjoyment. His legacy lives on and will inspire everyone. DAEDO!",
        }
    }

    # flow.state.token_metadata = {
    #     "memeTokenMetaData": {
    #         "name": "YONGCHANWOO_SCANDAL",
    #         "symbol": "YCWS",
    #         "Description": "YouTuber Yong Chan-woo (formerly known as 'Yonghosu') recently sparked outrage by mocking the late Daedoseogwan as a 'cocky high school graduate' and for his past controversial remark that 'Japan popularized Hangul during colonial rule.' The $YCWS token symbolizes both a warning against irresponsible speech and historical distortion, and a reminder of the delicate balance between freedom of expression and accountability.",
    #     }
    # }

    # flow.state.token_metadata = {
    #     "memeTokenMetaData": {
    #         "name": "Knife Attack at Jo Won-dong",
    #         "symbol": "KAJD",
    #         "description": "On September 3, 2025, a stabbing rampage occurred at a pizza franchise location in Jowon-dong (Sillim-dong), Gwanak-gu, Seoul. The franchise owner wielded a weapon against employees of an interior design company, killing three people and seriously injuring one. The incident is believed to have stemmed from a conflict with the franchise headquarters.",
    #     }
    # }
    # flow.state.token_metadata = {
    #     "memeTokenMetaData": {
    #         "name": "KESABANDAE",
    #         "symbol": "DDW",
    #         "Description": "The $DDW token is founded on the unyielding principle of 'rather perish than yield.' It aims to withstand external pressures for unreasonable change and preserve the community's unique identity and values. This transcends mere speculative meme coins, symbolizing the spirit of 'resistance and solidarity.'",
    #     }
    # }
    # flow.state.token_metadata = {
    #     "memeTokenMetaData": {
    #         "name": "LeagueOfCoin, $LCK",
    #         "symbol": "$LCK",
    #         "description": "Where Every Epic Match Deserves a Memecoin! As the LCK heats up like a fiery dragon in a 5v5 showdown, fans are more invested than ever. The excitement is palpable as teams like T1 and JustKnives clash, creating tension thicker than a tank's health bar. But why watch your favorite players when you can invest in their very own memecoin? Introducing $LCK — the coin that levels up your meme game while you cheer in front of your screen! Our beloved analysts are dissecting every play while fans passionately debate who deserves to be the ultimate champion. Meanwhile, somewhere on the interwebs, the $LCK is rising faster than a Ryze ultimate! We're here to take the throne, one meme at a time, while dodging the salt from fans who take losses harder than a Misfortune's Bullet Time!",
    #     }
    # }

    # flow.state.token_metadata = {
    #     "memeTokenMetaData": {
    #         "name": "90MinuteSlapCoin, $SLAP",
    #         "symbol": "$SLAP",
    #         "description": "Where a simple drama becomes a meme-worthy saga! The 'Marry My Husband' villain, known for her devious on-screen charisma, is now the star of a real-life plot twist. Fans are left reeling from claims of a 90-minute slap-fest and a mysterious 'forced transfer' from school. While the actress denies everything, the internet detectives are on the case, armed with popcorn and screenshots. This coin is for those who live for drama, where every accusation is a new chapter and every rebuttal is a cliffhanger. $SLAP is here to remind everyone that some stories just don't stay in the script! DAEDO!",
    #     }
    # }

    # flow.state.token_metadata = {
    #     "memeTokenMetaData": {
    #         "name": "PanicAttackCoin, $SJI",
    #         "symbol": "$SJI",
    #         "description": "25년차 국민 메인보컬의 멘탈 케어 밈코인! 코요태의 영원한 홍일점, 신지 누나가 겪었던 그 모든 고통을 기립니다. 살인적인 스케줄과 근거 없는 루머 속에서 묵묵히 마이크를 잡았던 그녀. 무대 위에서 쓰러지고 공황장애와 싸웠지만, $SJI는 '괜찮아질 거야'를 외치며 꿋꿋이 차트를 역주행합니다. 팬들의 응원과 함께 멘탈 회복이라는 궁극의 퀘스트를 완료한 그녀! 이제 $SJI는 우리의 멘탈까지 떡상시킬 준비가 됐습니다. 신지 화이팅!",
    #     }
    # }

    flow.run_website_developer()
    print(flow.state.website_url)


if __name__ == "__main__":
    kickoff()
