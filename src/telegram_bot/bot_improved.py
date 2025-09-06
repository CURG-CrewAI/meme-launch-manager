#!/usr/bin/env python
"""
개선된 Telegram Bot - 기존 코드 구조 유지하면서 개선
"""
import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from functools import wraps

# 기존 imports 유지
from meme_launch_manager.crews.trending_scraper.trending_scraper import TrendingScraperCrew
from meme_launch_manager.crews.meme_data_generator.meme_data_generator import MemeDataGeneratorCrew
from meme_launch_manager.crews.website_developer.website_developer import WebsiteDeveloper
from utils.bot_io import parse_trends_from_json
from html import escape as html_escape

# 새로 추가된 모듈
from storage_manager import StorageManager

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)


def with_error_handling(func):
    """에러 처리 데코레이터"""
    @wraps(func)
    async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            return await func(self, update, context)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            
            # 사용자에게 에러 메시지
            if update.callback_query:
                await update.callback_query.answer(
                    "오류가 발생했습니다. 다시 시도해주세요.", 
                    show_alert=True
                )
            elif update.message:
                await update.message.reply_text(
                    "⚠️ 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
                )
            
            # 락 해제 (있다면)
            if hasattr(self, '_current_lock_key'):
                self.storage.release_lock(self._current_lock_key)
                delattr(self, '_current_lock_key')
    
    return wrapper


class ImprovedMemeLaunchBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("No TELEGRAM_BOT_TOKEN")
        
        # Storage Manager 초기화
        self.storage = StorageManager()
        
        # Thread pool for CPU-bound tasks
        self.executor = ThreadPoolExecutor(max_workers=3)
        
        # Active jobs tracking (메모리)
        self.active_jobs: Dict[str, str] = {}
        
        print("IMPROVED TELEGRAM BOT INITIALIZED")
    
    @with_error_handling
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """시작 명령어 - 세션 생성 및 메뉴 표시"""
        user_id = str(update.effective_user.id)
        
        # 세션 생성/로드
        session = await self.storage.get_session(user_id)
        if not session:
            session = {
                'user_id': user_id,
                'username': update.effective_user.username,
                'credits': 5,
                'created_at': asyncio.get_event_loop().time()
            }
            await self.storage.set_session(user_id, session)
            
            welcome_text = (
                f"*환영합니다, {update.effective_user.first_name}님!* 🎉\n\n"
                "한국 실시간 트렌드 기반 밈코인 생성 봇입니다.\n"
                f"일일 생성 가능 횟수: {session['credits']}개\n\n"
                "아래에서 원하는 기능을 선택하세요."
            )
        else:
            # Rate limit 체크
            can_use, remaining = self.storage.check_rate_limit(user_id)
            welcome_text = (
                f"*다시 오신 것을 환영합니다!* 👋\n\n"
                f"오늘 남은 생성 횟수: {remaining}개\n\n"
                "무엇을 도와드릴까요?"
            )
        
        keyboard = [
            [InlineKeyboardButton("📊 최신 트렌드 보기", callback_data="get_latest_trends")],
            [InlineKeyboardButton("🔍 새로운 트렌드 분석", callback_data="start_analysis")],
            [InlineKeyboardButton("📜 내 토큰 목록", callback_data="my_tokens")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text, 
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    @with_error_handling
    async def get_latest_trends(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """캐시된 트렌드 또는 새로운 트렌드 가져오기"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(update.effective_user.id)
        
        # 캐시 확인
        cached_trends = self.storage.get_cache('trends:latest')
        
        if cached_trends:
            await self._show_trends(query, cached_trends, user_id, from_cache=True)
        else:
            # 캐시 없으면 파일에서 읽기
            try:
                trends = parse_trends_from_json()
                if trends:
                    # 캐시 저장 (10분)
                    self.storage.set_cache('trends:latest', trends, ttl=600)
                    await self._show_trends(query, trends, user_id, from_cache=False)
                else:
                    await query.edit_message_text(
                        "📭 저장된 트렌드가 없습니다.\n"
                        "새로운 분석을 시작해보세요!"
                    )
            except Exception as e:
                logger.error(f"Error loading trends: {e}")
                await query.edit_message_text("트렌드를 불러오는데 실패했습니다.")
    
    @with_error_handling
    async def start_analysis(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """새로운 트렌드 분석 시작 - 락과 진행상황 추적"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(update.effective_user.id)
        
        # Rate limit 체크
        can_use, remaining = self.storage.check_rate_limit(user_id)
        if not can_use:
            await query.edit_message_text(
                "⚠️ 일일 사용 한도를 초과했습니다.\n"
                "내일 다시 시도해주세요."
            )
            return
        
        # 락 체크 및 획득
        lock_key = f"{user_id}:analysis"
        if not self.storage.acquire_lock(lock_key, ttl=120):  # 2분 락
            await query.answer(
                "이미 분석이 진행 중입니다. 잠시만 기다려주세요.", 
                show_alert=True
            )
            return
        
        self._current_lock_key = lock_key
        job_id = str(uuid.uuid4())[:8]
        
        try:
            # 초기 메시지
            message = await query.edit_message_text(
                "🔍 *트렌드 분석을 시작합니다...*\n\n"
                f"작업 ID: `{job_id}`\n"
                "예상 소요 시간: 30-45초",
                parse_mode='Markdown'
            )
            
            # 진행 상황 추적 시작
            self.storage.update_progress(job_id, 'running', 10, '트렌드 수집 중...')
            
            # 비동기로 CrewAI 실행
            loop = asyncio.get_event_loop()
            
            # 진행 상황 업데이트 태스크
            update_task = asyncio.create_task(
                self._update_progress_message(message, job_id)
            )
            
            # CrewAI 실행 (별도 스레드에서)
            scraper_crew = TrendingScraperCrew()
            result = await loop.run_in_executor(
                self.executor,
                scraper_crew.crew().kickoff
            )
            
            # 진행 상황 업데이트 중지
            update_task.cancel()
            
            # 완료 상태 업데이트
            self.storage.update_progress(job_id, 'completed', 100, '분석 완료!')
            
            # 트렌드 파싱 및 캐시 저장
            trends = parse_trends_from_json()
            if trends:
                self.storage.set_cache('trends:latest', trends, ttl=600)
                
                # 세션 업데이트
                session = await self.storage.get_session(user_id)
                session['last_analysis'] = asyncio.get_event_loop().time()
                await self.storage.set_session(user_id, session)
                
                # 사용량 증가
                self.storage.increment_usage(user_id)
                
                # 결과 표시
                await self._show_trends(query, trends, user_id, from_cache=False)
            else:
                await message.edit_text("분석은 완료했지만 트렌드를 찾지 못했습니다.")
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            self.storage.update_progress(job_id, 'failed', 0, str(e))
            await query.edit_message_text(
                f"❌ 분석 중 오류가 발생했습니다.\n"
                f"오류: {str(e)[:100]}"
            )
        finally:
            # 락 해제
            self.storage.release_lock(lock_key)
            if hasattr(self, '_current_lock_key'):
                delattr(self, '_current_lock_key')
    
    async def _update_progress_message(self, message, job_id: str):
        """진행 상황 메시지 업데이트"""
        progress_messages = [
            (20, "📰 나무뉴스 트렌드 수집 중..."),
            (40, "🐦 X(트위터) 트렌드 수집 중..."),
            (60, "🔍 구글 트렌드 수집 중..."),
            (80, "📊 데이터 정리 중..."),
            (90, "✍️ 트렌드 설명 생성 중...")
        ]
        
        try:
            for progress, msg in progress_messages:
                await asyncio.sleep(5)  # 5초마다 업데이트
                
                # 진행 상황 저장
                self.storage.update_progress(job_id, 'running', progress, msg)
                
                # 메시지 업데이트
                await message.edit_text(
                    f"🔍 *트렌드 분석 진행 중...*\n\n"
                    f"작업 ID: `{job_id}`\n"
                    f"진행률: {progress}%\n"
                    f"현재: {msg}",
                    parse_mode='Markdown'
                )
        except asyncio.CancelledError:
            pass
    
    async def _show_trends(self, query, trends: list, user_id: str, from_cache: bool = False):
        """트렌드 목록 표시"""
        # 세션에 트렌드 저장
        session = await self.storage.get_session(user_id)
        session['trends'] = trends
        await self.storage.set_session(user_id, session)
        
        # 키보드 생성
        keyboard = []
        for idx, trend in enumerate(trends[:10]):
            keyword = trend.get('keyword', 'Unknown')
            keyboard.append([
                InlineKeyboardButton(
                    f"{idx + 1}. {keyword}", 
                    callback_data=f"select_trend_{idx}"
                )
            ])
        
        # 새로고침 버튼 추가
        keyboard.append([
            InlineKeyboardButton(
                "🔄 새로고침", 
                callback_data="start_analysis"
            )
        ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        cache_indicator = "📦 (캐시됨)" if from_cache else "✨ (새로운)"
        
        await query.edit_message_text(
            f"*🇰🇷 한국 실시간 트렌드* {cache_indicator}\n\n"
            "밈코인을 생성할 키워드를 선택하세요:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    @with_error_handling
    async def select_trend(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """트렌드 선택 및 메타데이터 생성"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(update.effective_user.id)
        trend_idx = int(query.data.split("_")[-1])
        
        # 세션에서 트렌드 가져오기
        session = await self.storage.get_session(user_id)
        if not session or 'trends' not in session:
            await query.edit_message_text("세션이 만료되었습니다. 다시 시작해주세요.")
            return
        
        selected_trend = session['trends'][trend_idx]
        keyword = selected_trend.get('keyword', 'Unknown')
        
        # 락 획득
        lock_key = f"{user_id}:metadata:{keyword}"
        if not self.storage.acquire_lock(lock_key, ttl=90):
            await query.answer("이미 처리 중입니다.", show_alert=True)
            return
        
        try:
            # 캐시 확인
            cache_key = f"metadata:{keyword}"
            cached_metadata = self.storage.get_cache(cache_key)
            
            if cached_metadata:
                # 캐시된 메타데이터 사용
                await self._show_metadata(query, keyword, cached_metadata, user_id, trend_idx)
            else:
                # 새로 생성
                await query.edit_message_text(
                    f"🎨 *{keyword}* 밈코인 메타데이터 생성 중...\n"
                    f"예상 소요 시간: 30초",
                    parse_mode='Markdown'
                )
                
                # CrewAI 실행
                inputs = {
                    "keyword": selected_trend["keyword"],
                    "why_trending": selected_trend.get("why_trending", ""),
                }
                
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    lambda: MemeDataGeneratorCrew().crew().kickoff(inputs=inputs)
                )
                
                metadata_text = result.raw
                
                # 캐시 저장
                self.storage.set_cache(cache_key, metadata_text, ttl=3600)
                
                # R2에 저장
                token_id = str(uuid.uuid4())
                await self.storage.save_to_r2(
                    f"tokens/{token_id}/metadata.json",
                    {
                        'keyword': keyword,
                        'metadata': metadata_text,
                        'user_id': user_id,
                        'created_at': asyncio.get_event_loop().time()
                    }
                )
                
                # 세션 업데이트
                session['last_token_id'] = token_id
                session['metadata'] = metadata_text
                await self.storage.set_session(user_id, session)
                
                await self._show_metadata(query, keyword, metadata_text, user_id, trend_idx)
                
        finally:
            self.storage.release_lock(lock_key)
    
    async def _show_metadata(self, query, keyword: str, metadata: str, user_id: str, trend_idx: int):
        """메타데이터 표시"""
        escaped_meta = html_escape(metadata[:500])  # 처음 500자만
        
        result_message = (
            f"<b>✅ {html_escape(keyword)} 밈토큰 메타데이터 생성 완료!</b>\n\n"
            f"<blockquote expandable>{escaped_meta}...</blockquote>"
        )
        
        keyboard = [
            [InlineKeyboardButton("🔄 다시 생성", callback_data=f"select_trend_{trend_idx}")],
            [InlineKeyboardButton("🌐 웹사이트 생성", callback_data=f"generate_website_{trend_idx}")],
            [InlineKeyboardButton("🪙 토큰 발행", callback_data=f"create_token_{trend_idx}")],
            [InlineKeyboardButton("◀️ 트렌드 목록", callback_data="get_latest_trends")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            result_message,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    @with_error_handling
    async def my_tokens(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """사용자의 토큰 목록 표시"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(update.effective_user.id)
        
        # R2에서 사용자 토큰 목록 가져오기 (실제로는 더 복잡한 로직 필요)
        await query.edit_message_text(
            "🪙 *내 토큰 목록*\n\n"
            "아직 생성된 토큰이 없습니다.\n"
            "트렌드를 선택하여 첫 토큰을 만들어보세요!",
            parse_mode='Markdown'
        )
    
    def run(self):
        """봇 실행"""
        application = Application.builder().token(self.bot_token).build()
        
        # 핸들러 등록
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.start_analysis, pattern="start_analysis"))
        application.add_handler(CallbackQueryHandler(self.get_latest_trends, pattern="get_latest_trends"))
        application.add_handler(CallbackQueryHandler(self.select_trend, pattern="select_trend_"))
        application.add_handler(CallbackQueryHandler(self.my_tokens, pattern="my_tokens"))
        
        print("🚀 Improved Meme Launch Manager Bot started.")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    bot = ImprovedMemeLaunchBot()
    bot.run()


if __name__ == "__main__":
    main()
