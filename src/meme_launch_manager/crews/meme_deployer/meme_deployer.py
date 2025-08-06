from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileWriterTool, DallETool
from typing import List
from meme_launch_manager.tools.download_image_tool import DownloadImageTool

# DALL·E Tool
dalle_tool = DallETool(model="dall-e-3", size="1024x1024", quality="standard", n=1)


@CrewBase
class MemeDeployerCrew:
    """MemeDeployerCrew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def token_meta_generator(self) -> Agent:
        # context 기반이므로 파일 입출력 도구 제거
        return Agent(config=self.agents_config["token_meta_generator"], verbose=True)

    @agent
    def visual_prompt_generator(self) -> Agent:
        # context 기반이므로 파일 입출력 도구 제거
        return Agent(config=self.agents_config["visual_prompt_generator"], verbose=True)

    @agent
    def image_generator(self) -> Agent:
        # 이미지 생성 → 저장 툴 필요
        return Agent(
            config=self.agents_config["image_generator"],
            tools=[dalle_tool, DownloadImageTool()],
            verbose=True,
        )

    @agent
    def metadata_assembler(self) -> Agent:
        return Agent(config=self.agents_config["metadata_assembler"], verbose=True)

    @task
    def generate_token_metadata(self) -> Task:
        return Task(config=self.tasks_config["generate_token_metadata"])

    @task
    def generate_image_prompt(self) -> Task:
        return Task(config=self.tasks_config["generate_image_prompt"])

    @task
    def generate_image_from_file(self) -> Task:
        return Task(config=self.tasks_config["generate_image_from_file"])

    @task
    def assemble_metadata(self) -> Task:
        return Task(config=self.tasks_config["assemble_metadata"])

    @crew
    def crew(self) -> Crew:
        """Creates the MemeDeployer crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
