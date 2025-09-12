from crewai import Agent, Crew, Task
from pydantic import BaseModel
from crewai.flow import Flow, listen, or_, router, start
from utils.image.download import download_image
from utils.image.nano_banana import edit_images_bytes
from utils.pages.deploy import deploy_site
from utils.pages.domain import add_domain
from utils.r2.uploads import upload_image, upload_json

from meme_launch_manager.crews.trending_scraper.trending_scraper import (
    TrendingScraperCrew,
)
from meme_launch_manager.crews.meme_data_generator.meme_data_generator import (
    MemeDataGeneratorCrew,
)
from meme_launch_manager.crews.website_developer.website_developer import (
    WebsiteDeveloper,
)


class MemeLaunchFlowState(BaseModel):
    top_trends: dict | None = None
    selected_trend: dict | None = None
    token_data: dict | None = None
    token_metadata: dict | None = None
    image_bytes: bytes | None = None
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
        total_token_datas = (
            MemeDataGeneratorCrew().crew().kickoff(inputs=selected_trend)
        )
        self.state.token_data = total_token_datas["memeTokenData"]
        self.state.token_metadata = total_token_datas["metadata"]
        self.io.send("\n===Basic Metadata===\n")
        self.io.send(
            f"Name: {self.state.token_metadata['name']}\nSymbol: {self.state.token_metadata['symbol']}\nDescription: {self.state.token_metadata['description']}"
        )

    @router(run_meme_data_generator)
    def ask_edit_image(self):
        image_flag = self.io.get_confirmation(
            "❔ Edit images? (default=N) (Y/N)", default=False
        )
        if image_flag:
            return "Image Edited"
        else:
            return "Image Not Edited"

    @listen("Image Edited")
    def run_image_generator(self):
        token_metadata = self.state.token_metadata
        self.io.send(
            "ℹ️ You can upload 2 images for editing\n\n  🙏 Please upload the images one by one 🙏"
        )
        image1_bytes = self.io.get_image(
            "❔ Please send the photo for editing.\n Waiting for the First photo…"
        )
        image2_bytes = self.io.get_image(
            "❔ Please send the photo for editing.\n Waiting for the Second photo…"
        )
        prompt = f"Read the following description and seamlessly composite the two photos. \nDescription:{token_metadata['description']}'"

        try:
            image_bytes = edit_images_bytes(prompt, image1_bytes, image2_bytes)
        except Exception as e:
            self.io.send(f"Image editing failed: {e!r}")
            raise

        self.state.image_bytes = image_bytes

    @listen("Image Not Edited")
    def get_image(self):
        image_bytes = self.io.get_image(
            "❔ Please send the photo for token image.\n Waiting for the photo…"
        )
        self.state.image_bytes = image_bytes

    @listen(or_(run_image_generator, get_image))
    def update_image_url_metadata(self):
        image_bytes = self.state.image_bytes
        token_metadata = self.state.token_metadata
        url = upload_image(image_bytes, self.state.id)
        if url:
            self.io.send("\n===Edited Image===\n")
            self.io.send(url)
            token_metadata["imgUrl"] = url
        else:
            self.io.send("nano-banana error")
            token_metadata["imgUrl"] = "/images/test-token.jpg"

    @router(update_image_url_metadata)
    def ask_make_website(self):
        website_flag = self.io.get_confirmation(
            "❔ Do you want to create and deploy a website? (default=N) (Y/N)"
        )
        if website_flag:
            return "Generated"
        else:
            return "Not Generated"

    @listen("Generated")
    def run_website_developer(self):
        token_data = self.state.token_data
        image_bytes = self.state.image_bytes
        download_image(image_bytes, "output/site/images", "token_image.jpg")
        WebsiteDeveloper().crew().kickoff(inputs={"token_metadata": token_data})
        self.state.website_url = deploy_site("output/site", "main", self.state.id)

    @listen(or_(run_website_developer, "Not Generated"))
    def update_website_url_metadata(self):
        url = self.state.website_url
        token_metadata = self.state.token_metadata
        if url:
            self.io.send("\n===Memetoken Website===\n")
            self.io.send(url)
            token_metadata["webUrl"] = url
        else:
            token_metadata["webUrl"] = "https://example.com"

    @listen(update_website_url_metadata)
    def update_telegram_url_metadata(self):
        url = self.io.get_text("❔ Telegram URL", "https://t.me/example")
        token_metadata = self.state.token_metadata
        token_metadata["telegramUrl"] = url

    @listen(update_telegram_url_metadata)
    def update_x_url_metadata(self):
        url = self.io.get_text("❔ X(twitter) URL", "https://twitter.com/example")
        token_metadata = self.state.token_metadata
        token_metadata["xUrl"] = url

    @listen(update_x_url_metadata)
    def finalize(self):
        token_metadata = self.state.token_metadata
        self.io.send("\n===🎉🎉🎉 Your MemeToken Metadata 🎉🎉🎉===\n")
        url = upload_json(token_metadata, self.state.id)
        self.io.send(url)

    def kickoff(self):
        try:
            super().kickoff()
        except TimeoutError:
            self.io.send("TimeOut")
        except Exception as e:
            self.io.send(f"Error")
            raise
