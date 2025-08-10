#!/usr/bin/env python
from __future__ import annotations

from pydantic import BaseModel, Field
from crewai.flow import Flow, listen, start

from meme_launch_manager.crews.trending_scraper.trending_scraper import (
    TrendingScraperCrew,
)
from meme_launch_manager.crews.meme_deployer.meme_deployer import MemeDeployerCrew

from utils.trends_io import load_trends_from_file, parse_raw_trends
from utils.cli import format_trends, prompt_choice, normalize_numeric
from utils.selection import validate_choice, pick_trend


# 플로우 스테이트 (트렌드 스크래핑해온 5개 저장 및 선택한 트렌드 저장)
class MemeLaunchFlowState(BaseModel):
    top_trends: list = Field(default_factory=list)
    selected_trend: dict | None = None


class MemeLaunchFlow(Flow[MemeLaunchFlowState]):

    # 트렌드를 스크래핑하고 플로우 스테이트에 담아서 다음 함수에게 전달
    @start()
    def run_scraping_crew(self):
        print("👀 Looking for trends in South Korea...")
        result = TrendingScraperCrew().crew().kickoff()
        trends = load_trends_from_file("output/trending_scraper/trends.json")
        if not trends:
            trends = parse_raw_trends(result.raw)

        self.state.top_trends = trends or []

    # 플로우 스테이트에 담겨있는 트렌드를 가지고 유저에게 입력 받음 -> CLI에 출력 및 다시 플로우 스테이트에 저장
    @listen(run_scraping_crew)
    def display_result(self):
        trends = self.state.top_trends
        if not trends:
            print("⚠️ There are no trends to display.")
            return

        print(format_trends(trends))

        # 현재 1~5가 아닌숫자나 문자등이 들어오면 무조건 1반환해서 생성하게 되어있음 나중에 루프 붙일때 수정 예정
        raw = prompt_choice("Choose the trend keyword number you want.", default=1)
        normalized = normalize_numeric(raw)

        if raw.strip() == "":
            print("⚠️ No input provided. Default (1) selected.")
        elif normalized is None:
            print("❌ Not a valid number. Default (1) selected.")

        choice = validate_choice(normalized, max_len=len(trends), default=1)
        if (normalized is not None) and (choice != normalized):
            print("❌ Invalid number. Default (1) selected.")

        selected = pick_trend(trends, choice)
        self.state.selected_trend = selected

        if selected:
            print(f"\n✅ Selected keyword: {selected.get('keyword','N/A')}")

    # 플로우스테이트에서 선택된 트렌드 확인후 밈토큰 메타데이터및 이미지 생성
    @listen(display_result)
    def run_meme_deployer(self):
        trend = self.state.selected_trend
        if not trend:
            print("⚠️ No trend selected")
            return

        inputs = {
            "keyword": trend["keyword"],
            "why_trending": trend["why_trending"],
        }
        result = MemeDeployerCrew().crew().kickoff(inputs=inputs)

        print("\n=== Final Meme Token Metadata ===\n")
        print(result.raw)


def kickoff():
    flow = MemeLaunchFlow()
    flow.kickoff()


def plot():
    flow = MemeLaunchFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
