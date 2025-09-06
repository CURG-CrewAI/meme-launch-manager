"""
Storage Manager for Telegram Bot
Handles KV, R2, and Redis operations
"""
import os
import json
import time
import redis
import httpx
import boto3
from typing import Any, Optional, Dict
from dotenv import load_dotenv

load_dotenv()


class StorageManager:
    """통합 스토리지 관리자 - KV, R2, Redis를 하나로"""
    
    def __init__(self):
        # Redis 연결 (Railway 자동 감지)
        redis_url = os.getenv('REDIS_URL')
        if redis_url:
            # Railway Redis URL 파싱
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
        else:
            # 로컬 개발용
            self.redis_client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                password=os.getenv('REDIS_PASSWORD'),
                decode_responses=True
            )
        
        # Cloudflare 설정
        self.cf_account_id = os.getenv('CF_ACCOUNT_ID')
        self.cf_api_token = os.getenv('CF_API_TOKEN')
        self.kv_namespace_id = os.getenv('KV_NAMESPACE_ID')
        
        # R2 설정 (S3 호환 API)
        self.r2_client = boto3.client(
            's3',
            endpoint_url=f'https://{self.cf_account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
            region_name='auto'
        )
        self.r2_bucket = os.getenv('R2_BUCKET_NAME')
    
    # ============ Session Management ============
    
    async def get_session(self, user_id: str) -> Optional[Dict]:
        """세션 가져오기 (Redis 우선, KV 폴백)"""
        # 1. Redis에서 먼저 확인 (빠름)
        session = self.redis_client.get(f"session:{user_id}")
        if session:
            return json.loads(session)
        
        # 2. KV에서 확인 (영구 저장)
        session = await self._kv_get(f"session:{user_id}")
        if session:
            # Redis에 캐시
            self.redis_client.setex(
                f"session:{user_id}",
                3600,  # 1시간
                json.dumps(session)
            )
            return session
        
        return None
    
    async def set_session(self, user_id: str, data: Dict, ttl: int = 3600):
        """세션 저장"""
        session_data = {
            **data,
            'updated_at': time.time()
        }
        
        # Redis에 저장
        self.redis_client.setex(
            f"session:{user_id}",
            ttl,
            json.dumps(session_data)
        )
        
        # KV에도 저장 (백업)
        await self._kv_put(f"session:{user_id}", session_data, ttl)
    
    # ============ Lock Management ============
    
    def acquire_lock(self, key: str, ttl: int = 60) -> bool:
        """락 획득 (Redis 사용)"""
        return self.redis_client.set(
            f"lock:{key}",
            "1",
            nx=True,  # Only set if not exists
            ex=ttl    # Expiration time
        )
    
    def release_lock(self, key: str):
        """락 해제"""
        self.redis_client.delete(f"lock:{key}")
    
    def is_locked(self, key: str) -> bool:
        """락 상태 확인"""
        return self.redis_client.exists(f"lock:{key}") > 0
    
    # ============ Cache Management ============
    
    def get_cache(self, key: str) -> Optional[Any]:
        """캐시 가져오기"""
        cached = self.redis_client.get(f"cache:{key}")
        if cached:
            data = json.loads(cached)
            # TTL 체크
            if time.time() - data.get('timestamp', 0) < data.get('ttl', 600):
                return data.get('value')
        return None
    
    def set_cache(self, key: str, value: Any, ttl: int = 600):
        """캐시 설정"""
        cache_data = {
            'value': value,
            'timestamp': time.time(),
            'ttl': ttl
        }
        self.redis_client.setex(
            f"cache:{key}",
            ttl,
            json.dumps(cache_data)
        )
    
    # ============ Progress Tracking ============
    
    def update_progress(self, job_id: str, status: str, progress: int = 0, message: str = ""):
        """작업 진행 상황 업데이트"""
        progress_data = {
            'job_id': job_id,
            'status': status,  # 'pending', 'running', 'completed', 'failed'
            'progress': progress,
            'message': message,
            'updated_at': time.time()
        }
        
        self.redis_client.setex(
            f"processing:{job_id}",
            300,  # 5분
            json.dumps(progress_data)
        )
    
    def get_progress(self, job_id: str) -> Optional[Dict]:
        """작업 진행 상황 조회"""
        progress = self.redis_client.get(f"processing:{job_id}")
        return json.loads(progress) if progress else None
    
    # ============ Rate Limiting ============
    
    def check_rate_limit(self, user_id: str, limit: int = 5) -> tuple[bool, int]:
        """일일 사용량 체크"""
        today = time.strftime('%Y-%m-%d')
        key = f"daily:{user_id}:{today}"
        
        current = self.redis_client.get(key)
        current_count = int(current) if current else 0
        
        if current_count >= limit:
            return False, limit - current_count
        
        return True, limit - current_count
    
    def increment_usage(self, user_id: str):
        """사용량 증가"""
        today = time.strftime('%Y-%m-%d')
        key = f"daily:{user_id}:{today}"
        
        pipe = self.redis_client.pipeline()
        pipe.incr(key)
        pipe.expire(key, 86400)  # 24시간
        pipe.execute()
    
    # ============ R2 Storage ============
    
    async def save_to_r2(self, key: str, data: Any):
        """R2에 데이터 저장"""
        try:
            if isinstance(data, dict):
                data = json.dumps(data, ensure_ascii=False)
            
            self.r2_client.put_object(
                Bucket=self.r2_bucket,
                Key=key,
                Body=data,
                ContentType='application/json'
            )
            return True
        except Exception as e:
            print(f"R2 save error: {e}")
            return False
    
    async def get_from_r2(self, key: str) -> Optional[Any]:
        """R2에서 데이터 가져오기"""
        try:
            response = self.r2_client.get_object(
                Bucket=self.r2_bucket,
                Key=key
            )
            data = response['Body'].read().decode('utf-8')
            return json.loads(data)
        except Exception as e:
            print(f"R2 get error: {e}")
            return None
    
    # ============ Private KV Methods ============
    
    async def _kv_get(self, key: str) -> Optional[Any]:
        """Cloudflare KV에서 값 가져오기"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.cloudflare.com/client/v4/accounts/{self.cf_account_id}/storage/kv/namespaces/{self.kv_namespace_id}/values/{key}",
                    headers={"Authorization": f"Bearer {self.cf_api_token}"}
                )
                if response.status_code == 200:
                    return response.json()
        except Exception as e:
            print(f"KV get error: {e}")
        return None
    
    async def _kv_put(self, key: str, value: Any, ttl: Optional[int] = None):
        """Cloudflare KV에 값 저장"""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "value": json.dumps(value) if isinstance(value, dict) else value
                }
                if ttl:
                    data["expiration_ttl"] = ttl
                
                await client.put(
                    f"https://api.cloudflare.com/client/v4/accounts/{self.cf_account_id}/storage/kv/namespaces/{self.kv_namespace_id}/values/{key}",
                    headers={"Authorization": f"Bearer {self.cf_api_token}"},
                    json=data
                )
        except Exception as e:
            print(f"KV put error: {e}")
