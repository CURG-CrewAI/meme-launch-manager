#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
import json
import ast
from pathlib import Path

from meme_launch_manager.crews.trending_scraper.trending_scraper import (
    TrendingScraperCrew,
)


class MemeLaunchFlowState(BaseModel):
    top_trends: list = []  # [{"keyword": "..."} ...]


class MemeLaunchFlow(Flow[MemeLaunchFlowState]):

    @start()
    def run_scraping_crew(self):
        print("👀 Looking for trends in South Korea...")
        result = TrendingScraperCrew().crew().kickoff()
        print("♻️", result.raw)
        print("✨", result)

        trends_file = Path("output/trending_scraper/trends.json")

        if trends_file.exists():
            try:
                with open(trends_file, "r", encoding="utf-8") as f:
                    self.state.top_trends = json.load(f)
                    print(f"📂 Loaded trends from {trends_file}")
                    return
            except json.JSONDecodeError as e:
                print("❌ Failed to parse trends.json:", e)

        raw_data = result.raw
        if not raw_data:
            print("⚠️ No output received from crew.")
            self.state.top_trends = []
        elif isinstance(raw_data, list):
            self.state.top_trends = raw_data
        elif isinstance(raw_data, str):
            try:
                self.state.top_trends = json.loads(raw_data)
            except json.JSONDecodeError:
                try:
                    self.state.top_trends = ast.literal_eval(raw_data)
                except (ValueError, SyntaxError):
                    print("❌ Failed to parse output.")
                    self.state.top_trends = []

    @listen(run_scraping_crew)
    def display_result(self):
        if not self.state.top_trends:
            print("⚠️ 표시할 트렌드 데이터가 없습니다.")
            return

        print("\n📢 Top trending keywords with reasons:\n")
        for idx, item in enumerate(self.state.top_trends, start=1):
            keyword = item.get("keyword", "N/A")
            reason = item.get("why_trending", "No explanation available.")
            print(f"{idx}. {keyword} — {reason}")

        # 선택 기능 추가
        try:
            choice = int(input("\n원하는 항목 번호를 선택하세요: "))
            if 1 <= choice <= len(self.state.top_trends):
                selected = self.state.top_trends[choice - 1]
                print(f"\n✅ 선택한 키워드: {selected['keyword']}")
                print(f"📖 이유: {selected['why_trending']}")
            else:
                print("❌ 잘못된 선택입니다.")
        except ValueError:
            print("❌ 숫자를 입력하세요.")


def kickoff():
    flow = MemeLaunchFlow()
    flow.kickoff()


def plot():
    flow = MemeLaunchFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
