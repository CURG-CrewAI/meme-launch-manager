#!/usr/bin/env python
from __future__ import annotations
import json
import os
from turtle import update

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
    website_url: str = False


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
            return "Not created"

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

    @listen(or_(update_website_url_metadata, "Not created"))
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


if __name__ == "__main__":
    kickoff()
