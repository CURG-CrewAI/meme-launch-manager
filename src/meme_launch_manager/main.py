from pydantic import BaseModel
from crewai.flow import Flow, listen, or_, router, start
from utils.image_helper import edit_images_bytes
from utils.metadata_helper import update_metadata

from meme_launch_manager.crews.trending_scraper.trending_scraper import (
    TrendingScraperCrew,
)
from meme_launch_manager.crews.meme_data_generator.meme_data_generator import (
    MemeDataGeneratorCrew,
)
from meme_launch_manager.crews.website_developer.website_developer import (
    WebsiteDeveloper,
)

import json


class MemeLaunchFlowState(BaseModel):
    top_trends: dict | None = None
    selected_trend: dict | None = None
    token_metadata: dict | None = None
    image_url: str | None = None
    website_url: str | None = None


class MemeLaunchFlow(Flow[MemeLaunchFlowState]):
    def __init__(self, io, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.io = io  # TelegramAdapter

    @start()
    def run_trending_scraper(self):
        self.io.send("👀 Looking for trends in South Korea...")
        top_trends = TrendingScraperCrew().crew().kickoff()
        self.io.send_trends(top_trends["trendsWithWhy"])
        self.state.top_trends = top_trends

    @listen(run_trending_scraper)
    def select_trend(self):
        top_trends = self.state.top_trends["trendsWithWhy"]
        self.state.selected_trend = self.io.get_trend_choice(top_trends, default=1)

    @listen(select_trend)
    def run_meme_data_generator(self):
        selected_trend = self.state.selected_trend
        token_metadata = MemeDataGeneratorCrew().crew().kickoff(inputs=selected_trend)
        self.io.send_json("output/metadata.json")
        self.state.token_metadata = token_metadata

    @router(run_meme_data_generator)
    def ask_edit_image(self):
        image_flag = self.io.get_confirmation("Edit images? (Y/N)", default=False)
        if image_flag:
            return "Image Edited"
        else:
            return "Image Not Edited"

    @listen("Image Edited")
    def run_image_generator(self):
        self.io.send(
            "You can upload 2 images for editing\n 🙏 Please upload the images one by one"
        )
        image1_bytes = self.io.get_image(
            "Please send the photo for editing.\n Waiting for the First photo…"
        )
        image2_bytes = self.io.get_image(
            "Please send the photo for editing.\n Waiting for the Second photo…"
        )
        prompt = (
            "사진의 인물이 화내고 있고, 다른 사진의 배경에 자연스럽게 합성해주세요."
        )
        try:
            out_bytes = edit_images_bytes(prompt, image1_bytes, image2_bytes)
        except Exception as e:
            self.io.send(f"Image editing failed: {e!r}")
            raise

        self.io.send_photo(
            out_bytes, filename="edited_image.jpg", caption="Editing Complete!"
        )
        self.state.image_url = "mock data"

    @listen("Image Not Edited")
    def get_image(self):
        image_bytes = self.io.get_image(
            "Please send the photo for token image.\n Waiting for the photo…"
        )
        self.state.image_url = "mock data"

    @listen(or_(run_image_generator, get_image))
    def update_image_url_metadata(self):
        url = self.state.image_url
        if url:
            update_metadata("output/metadata.json", "imgUrl", url)

    @router(update_image_url_metadata)
    def ask_make_website(self):
        website_flag = self.io.get_confirmation(
            "Do you want to create and deploy a website? (default={default}) (Y/N)"
        )
        if website_flag:
            return "Generated"
        else:
            return "Not Generated"

    @listen("Generated")
    def run_website_developer(self):
        token_metadata = self.state.token_metadata["memeTokenMetaData"]
        self.state.website_url = (
            WebsiteDeveloper().crew().kickoff(inputs={"token_metadata": token_metadata})
        )

    @listen(run_website_developer)
    def update_website_url_metadata(self):
        url = self.state.website_url
        if url:
            update_metadata("output/metadata.json", "WebUrl", url)

    @listen(or_(update_website_url_metadata, "Not Generated"))
    def update_telegram_url_metadata(self):
        url = self.io.get_text("Telegram URL:")
        if url:
            update_metadata("output/metadata.json", "telegramUrl", url)

    @listen(update_telegram_url_metadata)
    def update_x_url_metadata(self):
        url = self.io.get_text("X(twitter) URL:")
        if url:
            update_metadata("output/metadata.json", "xUrl", url)

    @listen(update_x_url_metadata)
    def finalize(self):
        self.io.send("\n===🎉🎉🎉 Your MemeToken Metadata 🎉🎉🎉===\n")
        self.io.send_json("output/metadata.json")

    def kickoff(self):
        try:
            super().kickoff()
        except TimeoutError:
            self.io.send("TimeOut")
        except Exception as e:
            self.io.send(f"Error")
            raise
