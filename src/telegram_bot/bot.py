#!/usr/bin/env python
import asyncio
import logging
from typing import Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from dotenv import load_dotenv

from meme_launch_manager.main import MemeLaunchFlow
from meme_launch_manager.crews.trending_scraper.trending_scraper import TrendingScraperCrew
from meme_launch_manager.crews.meme_data_generator.meme_data_generator import MemeDataGeneratorCrew
from meme_launch_manager.crews.website_developer.website_developer import WebsiteDeveloper
from utils.bot_io import parse_trends_from_json
from html import escape as html_escape

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

class MemeLaunchBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("No TELEGRAM_BOT_TOKEN")
        
        # TODO(@dokin) persist user states in database; this is a temporary solution
        self.user_states: Dict[int, Dict[str, Any]] = {}

        print("TELEGRAM BOT INITIALIZED")
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        welcome_text = (
            "*Meme Launch Manager Bot*\n\n"
            "Automatically creates memecoins based on real-time Korean trends.\n\n"
            "Select an option below to proceed."
        )
        
        keyboard = [
            [InlineKeyboardButton("View Latest Trends", callback_data="get_latest_trends")],
            [InlineKeyboardButton("Start Trend Analysis", callback_data="start_analysis")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def get_latest_trends(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id

        try: 
            trends = parse_trends_from_json()
            if not trends:
                await query.edit_message_text(
                    "No trends were found. Please try again."
                )
                return

            self.user_states[user_id] = {"trends": trends}
            
            keyboard = []
            for idx, trend in enumerate(trends[:10]):  # up to 10
                keyword = self.extract_keyword_from_trend(trend)
                keyboard.append([
                    InlineKeyboardButton(
                        f"{idx + 1}. {keyword}", 
                        callback_data=f"select_trend_{idx}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "*Current Trending Keywords in Korea*\n\n"
                "Select a keyword to generate a memecoin.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text(
                "An error occurred while fetching trends. Please try again."
            )

    async def start_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "Analyzing current Korean trends..."
        )
        
        try:
            scraper_crew = TrendingScraperCrew()
            await asyncio.get_event_loop().run_in_executor(
                None, scraper_crew.crew().kickoff
            )
            
            trends = parse_trends_from_json()
            
            if not trends:
                await query.edit_message_text(
                    "No trends were found. Please try again."
                )
                return
            
            user_id = update.effective_user.id
            self.user_states[user_id] = {"trends": trends}
            
            keyboard = []
            for idx, trend in enumerate(trends[:10]):
                keyword = self.extract_keyword_from_trend(trend)
                keyboard.append([
                    InlineKeyboardButton(
                        f"{idx + 1}. {keyword}", 
                        callback_data=f"select_trend_{idx}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "*Current Trending Keywords in Korea*\n\n"
                "Select a keyword to generate a memecoin.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text(
                "An error occurred during trend analysis. Please try again."
            )

    async def select_trend(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        trend_idx = int(query.data.split("_")[-1])

        if user_id not in self.user_states or "trends" not in self.user_states[user_id]:
            await query.edit_message_text(
                "Your session has expired. Please start over."
            )
            return
        
        selected_trend = self.user_states[user_id]["trends"][trend_idx]
        keyword = self.extract_keyword_from_trend(selected_trend)
        
        await query.edit_message_text(
            f"Selected trend: {keyword}\n\n"
            f"Generating memecoin metadata..."
        )
        
        try:
            inputs = {
                "keyword": selected_trend["keyword"],
                "why_trending": selected_trend["why_trending"],
            }
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: MemeDataGeneratorCrew().crew().kickoff(inputs=inputs)
            )
            
            metadata_text = result.raw
            escaped_meta = html_escape(metadata_text)

            self.user_states[user_id]["metadata"] = metadata_text
            result_message = (
                f"<b>Your meme token metadata generated for {html_escape(keyword)}.</b>\n\n"
                f"<blockquote expandable>{escaped_meta}</blockquote>"
            )

            keyboard = [
                [InlineKeyboardButton("Regenerate Metadata", callback_data=f"select_trend_{trend_idx}")],
                [InlineKeyboardButton("Generate Website", callback_data=f"generate_website_{trend_idx}")],
                [InlineKeyboardButton("Provide External URL", callback_data=f"external_url_{trend_idx}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                result_message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
                        
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text(
                "An error occurred while generating the memecoin. Please try again."
            )

    async def generate_website(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        trend_idx = int(query.data.split("_")[-1])
        
        if user_id not in self.user_states or "trends" not in self.user_states[user_id]:
            await query.edit_message_text(
                "Your session has expired. Please start over."
            )
            return
        
        await query.edit_message_text(
            "Building memecoin website..."
        )

        try:
            os.makedirs("output/moods", exist_ok=True)
            os.makedirs("output/site/images", exist_ok=True)
            await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda:  WebsiteDeveloper().crew().kickoff(inputs={"token_meta": self.user_states[user_id]["metadata"]})
            )
            
            website_url = None
            try:
                import json
                with open("output/deployment.json", "r") as f:
                    deployment_data = json.load(f)
                    website_url = deployment_data.get("site", {}).get("url")
                    print("ming website_url::", website_url)
            except Exception as e:
                print(f"Error reading deployment.json: {e}")
                website_url = None

        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text(
                "An error occurred while generating the website. Please try again."
            )
        
        # 웹사이트 생성 성공 메시지
        if website_url:
            success_message = (
                f"<b>Website generated successfully.</b>\n\n"
                f"Your meme token website: {website_url}\n\n"
                f"The website is now live and ready to use. You can regenerate the website by clicking the button below. If you want to provide an external URL and complete the metadata, you can do so by clicking the button below."
            )
            
            keyboard = [
                [InlineKeyboardButton("Visit Website", url=website_url)],
                [InlineKeyboardButton("Generate Another", callback_data=f"generate_website_{trend_idx}")],
                [InlineKeyboardButton("Provide External URL", callback_data=f"external_url_{trend_idx}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                success_message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(
                "Website generation completed, but URL could not be retrieved. Please check the logs."
            )

    def extract_keyword_from_trend(self, trend_data: Dict) -> str:
        if isinstance(trend_data, dict):
            return trend_data.get("keyword", "Unknown")
        else:
            return "Unknown"

    def run(self):
        application = Application.builder().token(self.bot_token).build()
        
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.start_analysis, pattern="start_analysis"))
        application.add_handler(CallbackQueryHandler(self.get_latest_trends, pattern="get_latest_trends"))
        application.add_handler(CallbackQueryHandler(self.select_trend, pattern="select_trend_"))
        application.add_handler(CallbackQueryHandler(self.generate_website, pattern="generate_website_"))
        
        print("Meme Launch Manager Bot started.")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    bot = MemeLaunchBot()
    bot.run()


if __name__ == "__main__":
    main()