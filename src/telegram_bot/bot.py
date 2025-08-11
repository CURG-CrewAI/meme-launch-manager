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
from utils.user_selectors import parse_trends_from_markdown

load_dotenv()

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

class MemeLaunchBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN이 환경변수에 설정되지 않았습니다.")
        
        # 사용자별 작업 상태 저장
        self.user_states: Dict[int, Dict[str, Any]] = {}

        print("TELEGRAM BOT INITIALIZED")
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        
        welcome_text = (
            "🚀 **Meme Launch Manager Bot**\n\n"
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
            trends = parse_trends_from_markdown()
            if not trends:
                await query.edit_message_text(
                    "❌ 트렌드를 찾을 수 없습니다. 다시 시도해주세요."
                )
                return
                        # 사용자 상태에 트렌드 저장
            self.user_states[user_id] = {"trends": trends}
            
            # 트렌드 선택 키보드 생성
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
                "📈 **현재 한국의 트렌딩 키워드**\n\n"
                "밈코인으로 만들고 싶은 트렌드를 선택해주세요:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        
        except Exception as e:
            logger.error(f"트렌드 분석 중 오류: {e}")
            await query.edit_message_text(
                "❌ 트렌드 분석 중 오류가 발생했습니다. 다시 시도해주세요."
            )

    async def start_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        # 분석 시작 메시지
        await query.edit_message_text(
            "👀 한국의 트렌드를 분석 중입니다...\n"
            "잠시만 기다려주세요. (약 1-2분 소요)"
        )
        
        try:
            scraper_crew = TrendingScraperCrew()
            await asyncio.get_event_loop().run_in_executor(
                None, scraper_crew.crew().kickoff
            )
            
            # 결과 파싱
            trends = parse_trends_from_markdown()
            
            if not trends:
                await query.edit_message_text(
                    "❌ 트렌드를 찾을 수 없습니다. 다시 시도해주세요."
                )
                return
            
            # 사용자 상태에 트렌드 저장
            self.user_states[user_id] = {"trends": trends}
            
            # 트렌드 선택 키보드 생성
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
                "📈 **현재 한국의 트렌딩 키워드**\n\n"
                "밈코인으로 만들고 싶은 트렌드를 선택해주세요:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"트렌드 분석 중 오류: {e}")
            await query.edit_message_text(
                "❌ 트렌드 분석 중 오류가 발생했습니다. 다시 시도해주세요."
            )

    async def select_trend(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        callback_data = query.data
        
        # 선택된 트렌드 인덱스 추출
        trend_idx = int(callback_data.split("_")[-1])
        print(f"trend_idx: {trend_idx}")
        
        if user_id not in self.user_states or "trends" not in self.user_states[user_id]:
            await query.edit_message_text(
                "❌ 세션이 만료되었습니다. /start로 다시 시작해주세요."
            )
            return
        
        selected_trend = self.user_states[user_id]["trends"][trend_idx]
        keyword = self.extract_keyword_from_trend(selected_trend)
        
        # 선택 확인 메시지
        await query.edit_message_text(
            f"✅ **선택된 트렌드**: {keyword}\n\n"
            f"🏗️ 밈코인 생성 중...\n"
            f"잠시만 기다려주세요. (약 2-3분 소요)"
        )
        
        try:
            result_message = (
                f"🎉 *밈코인 생성 완료\\!*\n\n"
                f"📊 *트렌드*: {keyword}\n"
                f"🪙 *토큰명*: MEME\\_{keyword.upper()[:6]}\n"
                f"💰 *초기 공급량*: 1,000,000,000\n"
                f"🔗 *컨트랙트 주소*: 0x..\n\n"
            )

            print("ming 1", result_message);
            
            keyboard = [
                [InlineKeyboardButton("🔄 새로운 트렌드 분석", callback_data="start_analysis")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text( # 이게 안됨
                result_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"밈코인 생성 중 오류: {e}")
            await query.edit_message_text(
                "❌ 밈코인 생성 중 오류가 발생했습니다. 다시 시도해주세요."
            )

    def extract_keyword_from_trend(self, trend_block: str) -> str:
        import re
        keyword_match = re.search(r"Keyword: (.+)", trend_block)
        return keyword_match.group(1) if keyword_match else "Unknown"

    def run(self):
        application = Application.builder().token(self.bot_token).build()
        
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.start_analysis, pattern="start_analysis"))
        application.add_handler(CallbackQueryHandler(self.get_latest_trends, pattern="get_latest_trends"))
        application.add_handler(CallbackQueryHandler(self.select_trend, pattern="select_trend_"))
        
        # 봇 실행
        print("🤖 Meme Launch Manager Bot이 시작되었습니다!")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """메인 엔트리 포인트"""
    bot = MemeLaunchBot()
    bot.run()


if __name__ == "__main__":
    main()
