from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileWriterTool, DallETool
from typing import List
from meme_launch_manager.tools.download_image_tool import DownloadImageTool
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

dalle_tool = DallETool(model="dall-e-3", size="1024x1024", quality="standard", n=1)
serper_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()
metadata_writer_tool = FileWriterTool(
    file_name="metadata.json", directory="output", overwrite=True
)

gemini_pro = LLM(model="gemini/gemini-2.5-pro")
gemini_flash = LLM(model="gemini/gemini-2.5-flash")
gemini_flash_lite = LLM(model="gemini/gemini-2.5-flash-lite")


@CrewBase
class MemeDataGeneratorCrew:
    """MemeDataGeneratorCrew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # @agent
    # def token_meta_generator(self) -> Agent:
    #     return Agent(config=self.agents_config["token_meta_generator"], verbose=True)

    @agent
    def news_url_collector(self) -> Agent:
        return Agent(
            config=self.agents_config["news_url_collector"],
            verbose=True,
            # llm=gemini_flash_lite,
            llm=gemini_flash,
            tools=[serper_tool],
        )

    @agent
    def article_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config["article_extractor"],
            verbose=True,
            llm=gemini_flash,
            tools=[scrape_tool],
        )

    @agent
    def satirist(self) -> Agent:
        return Agent(
            config=self.agents_config["satirist"],
            verbose=True,
            # llm=gemini_pro,
            llm=gemini_flash,
        )

    # @agent
    # def website_contents_writer(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config["website_contents_writer"],
    #         verbose=True,
    #         llm=self.gemini_pro,
    #     )

    @agent
    def json_converter(self) -> Agent:
        return Agent(
            config=self.agents_config["json_converter"],
            verbose=True,
            llm=gemini_flash,
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

    # @task
    # def generate_token_metadata(self) -> Task:
    #     return Task(config=self.tasks_config["generate_token_metadata"])

    @task
    def collect_news_url(self) -> Task:
        return Task(config=self.tasks_config["collect_news_url"])

    @task
    def extract_main_article(self) -> Task:
        return Task(
            config=self.tasks_config["extract_main_article"],
        )

    @task
    def write_satire(self) -> Task:
        return Task(
            config=self.tasks_config["write_satire"],
        )

    # @task
    # def write_website_contents(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["write_website_contents"],
    #     )

    @task
    def convert_json(self) -> Task:
        return Task(
            config=self.tasks_config["convert_json"],
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
