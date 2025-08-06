#!/usr/bin/env python
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
import json
import ast
from pathlib import Path
import unicodedata

from meme_launch_manager.crews.trending_scraper.trending_scraper import (
    TrendingScraperCrew,
)
from meme_launch_manager.crews.meme_deployer.meme_deployer import (
    MemeDeployerCrew,
)


class MemeLaunchFlowState(BaseModel):
    top_trends: list = []  # [{"keyword": "..."} ...]
    selected_trend: dict | None = None  # ✅ 선택한 트렌드 저장


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

        # 입력값 받기 + 정규화
        choice_str = input("\n원하는 항목 번호를 선택하세요 (기본=1): ").strip()
        print(f"[DEBUG] Raw input: {repr(choice_str)}")  # 입력값 디버그용 출력

        # 유니코드 숫자만 추출 (전각 포함)
        choice_str = "".join(
            ch for ch in choice_str if unicodedata.category(ch).startswith("N")
        )

        # 기본값 처리
        if not choice_str:
            choice = 1
            print("ℹ️ 입력이 없어서 기본값(1) 선택")
        else:
            try:
                choice = int(choice_str)
            except ValueError:
                print("❌ 숫자 형식이 아닙니다. 기본값(1) 선택")
                choice = 1

        # 선택 검증
        if 1 <= choice <= len(self.state.top_trends):
            self.state.selected_trend = self.state.top_trends[choice - 1]
            print(f"\n✅ 선택한 키워드: {self.state.selected_trend['keyword']}")
            print(f"📖 이유: {self.state.selected_trend['why_trending']}")
        else:
            print("❌ 잘못된 번호입니다. 기본값(1) 선택")
            self.state.selected_trend = self.state.top_trends[0]

    @listen(display_result)
    def run_meme_deployer(self):
        if self.state.selected_trend is None:  # ✅ 수정
            print("⚠️ 선택된 트렌드가 없습니다.")
            return

        inputs = {
            "keyword": self.state.selected_trend["keyword"],
            "why_trending": self.state.selected_trend["why_trending"],
        }
        result = MemeDeployerCrew().crew().kickoff(inputs=inputs)

        print("\n=== 최종 Meme Token Metadata ===\n")
        print(result.raw)  # 최종 딕셔너리 출력


def kickoff():
    flow = MemeLaunchFlow()
    flow.kickoff()


def plot():
    flow = MemeLaunchFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
