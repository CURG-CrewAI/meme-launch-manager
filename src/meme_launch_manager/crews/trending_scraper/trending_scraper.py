import sys, os
from dotenv import load_dotenv
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(BASE_DIR)

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileWriterTool, SeleniumScrapingTool, FileReadTool
from crewai_tools.tools.tavily_search_tool.tavily_search_tool import TavilySearchTool


# signal_scraping_tool = SeleniumScrapingTool(website_url='https://signal.bz/',css_element='.container',wait_time=5)
namunews_scraping_tool = SeleniumScrapingTool(
    website_url="https://namu.news/", wait_time=5
)
x_scraping_tool = SeleniumScrapingTool(
    website_url="https://getdaytrends.com/ko/korea/", css_element="#trends", wait_time=5
)
google_scraping_tool = SeleniumScrapingTool(
    website_url="https://trends.google.com/trending?geo=KR&hours=24",
    css_element=".enOdEe-wZVHld-zg7Cn",
    wait_time=5,
)

# signal_writer_tool = FileWriterTool(file_name="signal.md", directory="output", overwrite=True )
namunews_writer_tool = FileWriterTool(
    file_name="namunews.md", directory="output", overwrite=True
)
x_writer_tool = FileWriterTool(file_name="x.md", directory="output", overwrite=True)
google_writer_tool = FileWriterTool(
    file_name="google.md", directory="output", overwrite=True
)

namunews_read_tool = FileReadTool(file_path="../../output/namunews.md")
x_read_tool = FileReadTool(file_path="../../output/x.md")
google_read_tool = FileReadTool(file_path="../../output/google.md")
scrapped_site_read_tool = FileReadTool(file_path="../../output/scrapped_site.md")
trend_read_tool = FileReadTool(file_path="../../output/trend.md")


file_writer_tool = FileWriterTool(
    file_name="scrapped_site.md", directory="output", overwrite=True
)
trend_writer_tool = FileWriterTool(
    file_name="trend.md", directory="output", overwrite=True
)
final_writer_tool = FileWriterTool(
    file_name="final.md", directory="output", overwrite=True
)

tavily_tool = TavilySearchTool()

now_date = datetime.now().isoformat()


@CrewBase
class TrendingScraperCrew:
    """TrendingScraperCrew crew"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # === Agents ===
    @agent
    def namunews_trending_scraper(self) -> Agent:
        return Agent(
            config=self.agents_config["namunews_trending_scraper"],
            tools=[namunews_scraping_tool, namunews_writer_tool],
        )

    # @agent
    # def signal_trending_scraper(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config["signal_trending_scraper"],
    #         tools=[signal_scraping_tool, signal_writer_tool],
    #     )

    @agent
    def x_trending_crawler(self) -> Agent:
        return Agent(
            config=self.agents_config["x_trending_crawler"],
            tools=[x_scraping_tool, x_writer_tool],
        )

    @agent
    def google_trending_scraper(self) -> Agent:
        return Agent(
            config=self.agents_config["google_trending_scraper"],
            tools=[google_scraping_tool, google_writer_tool],
        )

    @agent
    def trending_organizer(self) -> Agent:
        return Agent(
            config=self.agents_config["trending_organizer"],
            tools=[x_read_tool, google_read_tool, namunews_read_tool, file_writer_tool],
        )

    @agent
    def cross_validation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["cross_validation_agent"],
            tools=[scrapped_site_read_tool, trend_writer_tool],
        )

    @agent
    def trend_explainer(self) -> Agent:
        return Agent(
            config=self.agents_config["trend_explainer"],
            tools=[trend_read_tool, final_writer_tool, tavily_tool],
        )

    # === Tasks ===
    @task
    def collect_namunews_trending(self) -> Task:
        return Task(config=self.tasks_config["collect_namunews_trending"])

    # @task
    # def collect_signal_trending(self) -> Task:
    #     return Task(config=self.tasks_config["collect_signal_trending"])

    @task
    def collect_x_trending(self) -> Task:
        return Task(config=self.tasks_config["collect_x_trending"])

    @task
    def collect_google_trending(self) -> Task:
        return Task(config=self.tasks_config["collect_google_trending"])

    @task
    def organize_trending(self) -> Task:
        return Task(config=self.tasks_config["organize_trending"])

    @task
    def cross_validate_trending(self) -> Task:
        return Task(config=self.tasks_config["cross_validate_trending"])

    @task
    def explain_trends(self) -> Task:
        return Task(config=self.tasks_config["explain_trends"])

    # === Crew ===
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
