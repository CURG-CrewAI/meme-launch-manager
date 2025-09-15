# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any, Dict, List
from crewai import LLM, Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileWriterTool, FileReadTool
from pydantic import BaseModel


catalog_cfg_reader_tool = FileReadTool(file_path="templates/catalog.json")

site_writer_tool = FileWriterTool(
    file_name="index.html", directory="output/site", overwrite=True
)

gemini_pro = LLM(model="gemini/gemini-2.5-pro")
# claude_pro = LLM(model="anthropic/claude-3-sonnet-20240229-v1:0")


class TokenMood(BaseModel):
    name: str
    mood_keywords: List[str]


class WebsiteStyle(BaseModel):
    name: str
    catalog: Dict[str, Any]


class WebsiteContents(BaseModel):
    name: str
    contents: str


@CrewBase
class WebsiteDeveloper:
    """WebsiteDeveloper crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    _agent_common = dict(
        allow_delegation=False,
        max_iter=2,
        max_rpm=10,
    )

    @agent
    def meme_mood_curator(self) -> Agent:
        return Agent(
            config=self.agents_config["meme_mood_curator"],
            **self._agent_common,
        )

    @agent
    def website_contents_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["website_contents_writer"],
            **self._agent_common,
        )

    @agent
    def design_recommender(self) -> Agent:
        return Agent(
            config=self.agents_config["design_recommender"],
            tools=[
                catalog_cfg_reader_tool,
            ],
            **self._agent_common,
        )

    @agent
    def meme_token_site_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["meme_token_site_designer"],
            tools=[
                site_writer_tool,
            ],
            **self._agent_common,
            llm=gemini_pro,
        )

    @task
    def extract_token_moods(self) -> Task:
        return Task(
            config=self.tasks_config["extract_token_moods"],
            async_execution=True,
            output_json=TokenMood,
        )

    @task
    def write_website_contents(self) -> Task:
        return Task(
            config=self.tasks_config["write_website_contents"],
            async_execution=True,
            output_json=WebsiteContents,
        )

    @task
    def select_layout_palette(self) -> Task:
        return Task(
            config=self.tasks_config["select_layout_palette"],
            context=[
                self.extract_token_moods(),
            ],
            output_json=WebsiteStyle,
        )

    @task
    def build_meme_token_sites(self) -> Task:
        return Task(
            config=self.tasks_config["build_meme_token_sites"],
            context=[
                self.select_layout_palette(),
                self.write_website_contents(),
            ],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
        )
