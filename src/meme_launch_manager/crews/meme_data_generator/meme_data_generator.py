from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileWriterTool, DallETool
from typing import List

from pydantic import BaseModel, Field
from meme_launch_manager.tools.download_image_tool import DownloadImageTool
from crewai_tools import SerperDevTool, ScrapeWebsiteTool


class Article(BaseModel):
    title: str
    url: str
    snippet: str
    source: str


class NewsArticles(BaseModel):
    keyword: str
    articles: List[Article]


class ArticleContent(BaseModel):
    title: str
    content: str
    key_points: List[str]
    background: str


class ExtractedContent(BaseModel):
    extracted_content: List[ArticleContent]


class MemeCoinMetaData(BaseModel):
    name: str
    symbol: str
    description: str
    features: List[str]
    warning: str
    hashtags: List[str]


metadata_writer_tool = FileWriterTool(
    file_name="metadata.json", directory="output", overwrite=True
)

# dalle_tool = DallETool(model="dall-e-3", size="1024x1024", quality="standard", n=1)
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

    @agent
    def news_url_collector(self) -> Agent:
        return Agent(
            config=self.agents_config["news_url_collector"],
            verbose=True,
            tools=[serper_tool],
        )

    @agent
    def article_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["article_extractor"],
            verbose=True,
            tools=[scrape_tool],
        )

    @agent
    def satirist(self) -> Agent:
        return Agent(
            config=self.agents_config["satirist"],
            verbose=True,
        )

    @agent
    def json_converter(self) -> Agent:
        return Agent(
            config=self.agents_config["json_converter"],
            verbose=True,
            tools=[metadata_writer_tool],
        )

    # @agent
    # def visual_prompt_generator(self) -> Agent:
    #     return Agent(config=self.agents_config["visual_prompt_generator"], verbose=True)

    # @agent
    # def image_generator(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config["image_generator"],
    #         tools=[dalle_tool, DownloadImageTool()],
    #         verbose=True,
    #     )

    # @agent
    # def metadata_assembler(self) -> Agent:
    #     return Agent(config=self.agents_config["metadata_assembler"], verbose=True)

    @task
    def collect_news_url(self) -> Task:
        return Task(
            config=self.tasks_config["collect_news_url"],
            output_json=NewsArticles,
        )

    @task
    def extract_main_article(self) -> Task:
        return Task(
            config=self.tasks_config["extract_main_article"],
            context=[self.collect_news_url()],
            output_json=ExtractedContent,
        )

    @task
    def write_satire(self) -> Task:
        return Task(
            config=self.tasks_config["write_satire"],
            context=[self.extract_main_article()],
        )

    @task
    def convert_json(self) -> Task:
        return Task(
            config=self.tasks_config["convert_json"],
            context=[self.write_satire()],
            output_json=MemeCoinMetaData,
        )

    # @task
    # def generate_image_prompt(self) -> Task:
    #     return Task(config=self.tasks_config["generate_image_prompt"])

    # @task
    # def generate_image_from_file(self) -> Task:
    #     return Task(config=self.tasks_config["generate_image_from_file"])

    # @task
    # def assemble_metadata(self) -> Task:
    #     return Task(config=self.tasks_config["assemble_metadata"])

    @crew
    def crew(self) -> Crew:
        """Creates the MemeDeployer crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
