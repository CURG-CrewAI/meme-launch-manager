#!/usr/bin/env python
from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start

from meme_launch_manager.crews.trending_scraper.trending_scraper import (
    TrendingScraperCrew,
)
from utils.user_selectors import user_select_trend_from_markdown


class MemeLaunchFlowState(BaseModel):
    selected_trend: str = ""


class MemeLaunchFlow(Flow[MemeLaunchFlowState]):

    @start()
    def run_scraping_crew(self):
        print("👀 Looking for trends in South Korea.")
        TrendingScraperCrew().crew().kickoff()

    @listen(run_scraping_crew)
    def user_select_trend(self):
        selected = user_select_trend_from_markdown()
        self.state.selected_trend = selected

    @listen(user_select_trend)
    def display_result(self):
        print("\n📢 The trending keyword you selected:\n")
        print(self.state.selected_trend)


def kickoff():
    flow = MemeLaunchFlow()
    flow.kickoff()


def plot():
    flow = MemeLaunchFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
