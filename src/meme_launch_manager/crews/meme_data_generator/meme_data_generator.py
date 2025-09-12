from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileWriterTool
from typing import Dict, List, Union

from pydantic import BaseModel, Field
from meme_launch_manager.tools.download_image_tool import DownloadImageTool
from crewai_tools import SerperDevTool, ScrapeWebsiteTool


class Article(BaseModel):
    title: str
    url: str
    snippet: str
    source: str


class TrendArticles(BaseModel):
    keyword: str
    articles: List[Article]


class Content(BaseModel):
    title: str
    content: str
    key_points: List[str]
    background: str


class ExtractedContent(BaseModel):
    extracted_content: List[Content]


class Source(BaseModel):
    outlet: str
    title: str
    url: str


class IssueSummary(BaseModel):
    title: str
    key_visual_keywords: List[str]
    background: str
    what_happened: str
    key_points: List[str]
    why_it_matters: str


class Summary(BaseModel):
    korean_issue_summary: IssueSummary
    sources: List[Source]


class Description(BaseModel):
    description: str


class Satire(BaseModel):
    name: str
    symbol: List[str]
    catchphrase: str
    satire: str
    feature: List[str]
    hashtags: str


class Datas(BaseModel):
    name: str
    symbol: str
    catchphrase: str
    satire: str
    feature: List[str]
    hashtags: List[str]
    description: str
    korean_issue_summary: IssueSummary
    sources: List[Source]


class Metadata(BaseModel):
    name: str
    symbol: str
    description: str
    sources: List[Source]


class MemeTokenMetaData(BaseModel):
    memeTokenData: Datas
    metadata: Metadata


metadata_writer_tool = FileWriterTool(
    file_name="metadata.json", directory="output", overwrite=True
)

serper_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

gemini_pro = LLM(model="gemini/gemini-2.5-pro")
gemini_flash = LLM(model="gemini/gemini-2.5-flash")
gemini_flash_lite = LLM(model="gemini/gemini-2.5-flash-lite")


@CrewBase
class MemeDataGeneratorCrew:
    """MemeDataGeneratorCrew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    _agent_common = dict(
        allow_delegation=False,
        max_iter=2,
        max_rpm=10,
    )

    @agent
    def news_url_collector(self) -> Agent:
        return Agent(
            config=self.agents_config["news_url_collector"],
            verbose=True,
            tools=[serper_tool],
            **self._agent_common,
        )

    @agent
    def article_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["article_extractor"],
            verbose=True,
            tools=[scrape_tool],
            **self._agent_common,
        )

    @agent
    def summary_translation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["summary_translation_agent"],
            verbose=True,
            **self._agent_common,
        )

    @agent
    def description_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["description_writer"],
            verbose=True,
        )

    @agent
    def satirist(self) -> Agent:
        return Agent(
            config=self.agents_config["satirist"],
            verbose=True,
        )

    @agent
    def data_organizer(self) -> Agent:
        return Agent(
            config=self.agents_config["data_organizer"],
            verbose=True,
            tools=[metadata_writer_tool],
        )

    @task
    def collect_news_url(self) -> Task:
        return Task(
            config=self.tasks_config["collect_news_url"],
            output_json=TrendArticles,
        )

    @task
    def extract_main_article(self) -> Task:
        return Task(
            config=self.tasks_config["extract_main_article"],
            context=[self.collect_news_url()],
            output_json=ExtractedContent,
        )

    @task
    def translate_summarize_articles(self) -> Task:
        return Task(
            config=self.tasks_config["translate_summarize_articles"],
            context=[self.extract_main_article()],
            output_json=Summary,
        )

    @task
    def write_description(self) -> Task:
        return Task(
            config=self.tasks_config["write_description"],
            context=[self.translate_summarize_articles()],
            output_json=Description,
            # async_execution=True,
        )

    @task
    def write_satire(self) -> Task:
        return Task(
            config=self.tasks_config["write_satire"],
            context=[self.translate_summarize_articles()],
            output_json=Satire,
            # async_execution=True,
        )

    @task
    def organize_datas(self) -> Task:
        return Task(
            config=self.tasks_config["organize_datas"],
            context=[
                self.write_satire(),
                self.write_description(),
                self.translate_summarize_articles(),
            ],
            output_json=MemeTokenMetaData,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MemeDeployer crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
