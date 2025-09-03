#!/usr/bin/env python
from __future__ import annotations
import json
import os

from pydantic import BaseModel, Field
from crewai.flow import Flow, listen, start

from meme_launch_manager.crews.trending_scraper.trending_scraper import (
    TrendingScraperCrew,
)
from meme_launch_manager.crews.meme_data_generator.meme_data_generator import (
    MemeDataGeneratorCrew,
)
from meme_launch_manager.crews.website_developer.website_developer import (
    WebsiteDeveloper,
)

from utils.metadata_manager import print_metadata
from utils.trends_io import load_trends_from_file, parse_raw_trends
from utils.cli import print_trends, prompt_choice_trend, prompt_make_site


# 플로우 스테이트 (트렌드 스크래핑해온 5개 저장 및 선택한 트렌드 저장 and 웹사이트 생성 찬반, 토큰메타데이터 저장)
class MemeLaunchFlowState(BaseModel):
    top_trends: dict | None = None
    selected_trend: dict | None = None
    make_website: bool = False
    token_meta: dict | None = None


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
        print(f"{self.state.selected_trend}")

    @listen(select_trend)
    def run_meme_data_generator(self):
        selected_trend = self.state.selected_trend

        inputs = {
            "keyword": selected_trend["keyword"],
            "why_trending": selected_trend["why_trending"],
        }
        result = MemeDataGeneratorCrew().crew().kickoff(inputs=inputs)

        meta = result.raw
        if isinstance(meta, str):
            try:
                meta = json.loads(meta)
            except Exception:
                meta = {"raw": result.raw}

        self.state.token_meta = meta
        print("\n=== Basic Meme Token Metadata ===\n")
        print_metadata("output/metadata.json")

    # 웹사이트 생성 물어보기 -> 만드는지 안만드는지 bool로 저장
    @listen(run_meme_data_generator)
    def ask_make_website(self):
        self.state.make_website = prompt_make_site(
            "Do you want to create and deploy a website?", default="n"
        )
        print(f"🌐 Website generation: {'ON' if self.state.make_website else 'OFF'}")

    # 웹사이트 생성 <- 토큰 메타데이터 받아서 사이트 생성
    @listen(ask_make_website)
    def maybe_build_website(self):
        if not self.state.make_website:
            print("⚠️ Website generation skipped.")
            return
        if not self.state.token_meta:
            print("⚠️ No token metadata in memory.")
            return

        os.makedirs("output/moods", exist_ok=True)
        os.makedirs("output/site/images", exist_ok=True)

        print("🌐 Building & deploying meme token website...")
        WebsiteDeveloper().crew().kickoff(inputs={"token_meta": self.state.token_meta})
        print("\n=== Advanced Meme Token Metadata ===\n")
        print_metadata("output/metadata.json")


def kickoff():
    flow = MemeLaunchFlow()
    flow.kickoff()


def plot():
    flow = MemeLaunchFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
