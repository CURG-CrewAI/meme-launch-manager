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
from meme_launch_manager.crews.meme_deployer.meme_deployer import MemeDeployerCrew
from utils.bot_io import parse_trends_from_json

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
        
        self.user_states: Dict[int, Dict[str, Any]] = {} #TODO(@dokin) you must save user states in database it is temporary solution

        print("TELEGRAM BOT INITIALIZED")
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        
        welcome_text = (
            "🚀 *Meme Launch Manager Bot*\n\n"
            "한국의 실시간 트렌드를 기반으로 밈코인을 자동 생성합니다!\n\n"
            "아래 버튼을 클릭하여 트렌드 분석을 시작하세요:"
        )
        
        keyboard = [
            [InlineKeyboardButton("📈 최신 트렌드 보기", callback_data="get_latest_trends")],
            [InlineKeyboardButton("🔍 트렌드 분석 시작", callback_data="start_analysis")]
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
                    "트렌드를 찾을 수 없습니다. 다시 시도해주세요."
                )
                return

            self.user_states[user_id] = {"trends": trends}
            
            keyboard = []
            for idx, trend in enumerate(trends[:10]):  # 최대 10개만 표시
                keyword = self.extract_keyword_from_trend(trend)
                keyboard.append([
                    InlineKeyboardButton(
                        f"{idx + 1}. {keyword}", 
                        callback_data=f"select_trend_{idx}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📈 *현재 한국의 트렌딩 키워드*\n\n"
                "밈코인으로 만들고 싶은 트렌드를 선택해주세요",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text(
                "트렌드 분석 중 오류가 발생했습니다. 다시 시도해주세요."
            )

    async def start_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        await query.edit_message_text(
            "👀 한국의 트렌드를 분석 중입니다...\n"
        )
        
        try:
            scraper_crew = TrendingScraperCrew()
            await asyncio.get_event_loop().run_in_executor(
                None, scraper_crew.crew().kickoff
            )
            
            trends = parse_trends_from_json()
            
            if not trends:
                await query.edit_message_text(
                    "트렌드를 찾을 수 없습니다. 다시 시도해주세요."
                )
                return
            
            self.user_states[user_id] = {"trends": trends}
            
            keyboard = []
            for idx, trend in enumerate(trends[:10]):  # 최대 10개만 표시
                keyword = self.extract_keyword_from_trend(trend)
                keyboard.append([
                    InlineKeyboardButton(
                        f"{idx + 1}. {keyword}", 
                        callback_data=f"select_trend_{idx}"
                    )
                ])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📈 *현재 한국의 트렌딩 키워드*\n\n"
                "밈코인으로 만들고 싶은 트렌드를 선택해주세요",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text(
                "트렌드 분석 중 오류가 발생했습니다. 다시 시도해주세요."
            )

    async def select_trend(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        callback_data = query.data
        
        trend_idx = int(callback_data.split("_")[-1])
        print(f"trend_idx: {trend_idx}")
        
        if user_id not in self.user_states or "trends" not in self.user_states[user_id]:
            await query.edit_message_text(
                "세션이 만료되었습니다. 다시 시작해주세요."
            )
            return
        
        selected_trend = self.user_states[user_id]["trends"][trend_idx]
        keyword = self.extract_keyword_from_trend(selected_trend)
        
        await query.edit_message_text(
            f"✅ **선택된 트렌드**: {keyword}\n\n"
            f"🏗️ 밈코인 메타 데이터 생성 중...\n"
        )
        
        try:
            inputs = {
                "keyword": selected_trend["keyword"],
                "why_trending": selected_trend["why_trending"],
            }
            
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: MemeDeployerCrew().crew().kickoff(inputs=inputs)
            )
            
            metadata_text = result.raw
            print(f"Generated metadata: {metadata_text}")
            self.user_states[user_id]["metadata"] = metadata_text
            
            result_message = (
                f"🎉 *{keyword} 밈코인 메타 데이터 생성 완료\\!*\n\n"
                f"```\n{metadata_text}\n```\n\n"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔄 메타 데이터 다시 만들기", callback_data=f"regenerate_metadata_{trend_idx}")],
                [InlineKeyboardButton("⏩️ 웹사이트 생성하기", callback_data=f"generate_website_{trend_idx}")],
                [InlineKeyboardButton("🔀 외부 URL 입력하기", callback_data=f"external_url_{trend_idx}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                result_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text(
                "밈코인 생성 중 오류가 발생했습니다. 다시 시도해주세요."
            )

    async def regenerate_metadata(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        callback_data = query.data
        
        trend_idx = int(callback_data.split("_")[-1])
        
        if user_id not in self.user_states or "trends" not in self.user_states[user_id]:
            await query.edit_message_text(
                "세션이 만료되었습니다. 다시 시작해주세요."
            )
            return
        
        selected_trend = self.user_states[user_id]["trends"][trend_idx]
        keyword = self.extract_keyword_from_trend(selected_trend)
        
        await query.edit_message_text(
            f"🔄 *{keyword} 메타 데이터 재생성 중...*\n\n"
        )
        
        try:
            inputs = {
                "keyword": selected_trend["keyword"],
                "why_trending": selected_trend["why_trending"],
            }
            
            # 비동기 실행을 위해 executor 사용
            result = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: MemeDeployerCrew().crew().kickoff(inputs=inputs)
            )
            
            metadata_text = result.raw
            print(f"Regenerated metadata: {metadata_text}")
            
            result_message = (
                f"🎉 *{keyword} 밈코인 메타 데이터 재생성 완료\\!*\n\n"
                f"```\n{metadata_text}\n```\n\n"
            )
            
            keyboard = [
                [InlineKeyboardButton("🔄 메타 데이터 다시 만들기", callback_data=f"regenerate_metadata_{trend_idx}")],
                [InlineKeyboardButton("⏩️ 웹사이트 생성하기", callback_data=f"generate_website_{trend_idx}")],
                [InlineKeyboardButton("🔀 외부 URL 입력하기", callback_data=f"external_url_{trend_idx}")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                result_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.edit_message_text(
                "메타 데이터 재생성 중 오류가 발생했습니다. 다시 시도해주세요."
            )

    async def generate_website(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        callback_data = query.data
        
        trend_idx = int(callback_data.split("_")[-1])
        
        if user_id not in self.user_states or "trends" not in self.user_states[user_id]:
            await query.edit_message_text(
                "세션이 만료되었습니다. 다시 시작해주세요."
            )
            return
        
        await query.edit_message_text(
            f"🏗️ 밈코인 웹사이트 생성 중...\n"
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
        application.add_handler(CallbackQueryHandler(self.regenerate_metadata, pattern="regenerate_metadata_"))
        application.add_handler(CallbackQueryHandler(self.generate_website, pattern="generate_website_"))
        
        print("🤖 Meme Launch Manager Bot이 시작되었습니다!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    bot = MemeLaunchBot()
    bot.run()


if __name__ == "__main__":
    main()
