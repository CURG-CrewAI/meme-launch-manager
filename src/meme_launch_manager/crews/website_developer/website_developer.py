# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import shutil
from typing import List


from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task, after_kickoff
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import FileWriterTool, FileReadTool
from utils.metadata_manager import add_metadata

from utils.deploy_website import deploy_sites_under

layouts_cfg_reader_tool = FileReadTool(file_path="templates/layouts.json")
palettes_cfg_reader_tool = FileReadTool(file_path="templates/palettes.json")

site_writer_tool = FileWriterTool(
    file_name="index.html", directory="output/site", overwrite=True
)
mood_writer_tool = FileWriterTool(
    file_name="token_mood.json", directory="output/moods", overwrite=True
)
website_contents_writer_tool = FileWriterTool(
    file_name="website_contents.txt", directory="output/site", overwrite=True
)
selected_design_writer_tool = FileWriterTool(
    file_name="selected_designs.json", directory="output/moods", overwrite=True
)
md_writer_tool = FileWriterTool(
    file_name="DESIGN_RATIONALE.md", directory="output/site", overwrite=True
)


@CrewBase
class WebsiteDeveloper:
    """WebsiteDeveloper crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def _copy_token_image(self, symbol: str = "") -> None:
        src = "output/images/token_image.png"
        dst_dir = f"output/site/images"
        if os.path.exists(src):
            os.makedirs(dst_dir, exist_ok=True)
            shutil.copy(src, dst_dir)
            print(f"🖼 Copied token_image.png → {dst_dir}")
        else:
            print(f"⚠️ Token image not found at {src}")

    @after_kickoff
    def deploy_to_cloudflare_pages(self, output) -> None:
        sites_dir = "output/site"
        try:
            os.makedirs(os.path.join(sites_dir, "images"), exist_ok=True)
            self._copy_token_image()
        except Exception as e:
            print(f"⚠️ Image copy failed: {e}")
        url=deploy_sites_under(
            sites_dir=sites_dir,
            image_copier=None,
            branch="main",
            report_path="output/deployment.json",
        )
        add_metadata("output/metadata.json", "Website", url)

        

    @agent
    def meme_mood_curator(self) -> Agent:
        return Agent(
            config=self.agents_config["meme_mood_curator"],
            tools=[mood_writer_tool],
        )

    @agent
    def website_contents_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["website_contents_writer"],
            tools=[website_contents_writer_tool],
        )

    @agent
    def design_recommender(self) -> Agent:
        return Agent(
            config=self.agents_config["design_recommender"],
            tools=[
                layouts_cfg_reader_tool,
                palettes_cfg_reader_tool,
                selected_design_writer_tool,
            ],
        )

    @agent
    def meme_token_site_designer(self) -> Agent:
        return Agent(
            config=self.agents_config["meme_token_site_designer"],
            tools=[
                layouts_cfg_reader_tool,
                palettes_cfg_reader_tool,
                site_writer_tool,
                md_writer_tool,
            ],
        )

    @task
    def extract_token_moods(self) -> Task:
        return Task(config=self.tasks_config["extract_token_moods"])

    @task
    def write_website_contents(self) -> Task:
        return Task(config=self.tasks_config["write_website_contents"])

    @task
    def select_layout_palette(self) -> Task:
        return Task(config=self.tasks_config["select_layout_palette"])

    @task
    def build_meme_token_sites(self) -> Task:
        return Task(config=self.tasks_config["build_meme_token_sites"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
