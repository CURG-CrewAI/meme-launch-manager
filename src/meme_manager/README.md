# Four.meme Token Creation SDK (Python)

Four.meme 플랫폼에서 토큰을 생성하기 위한 Python SDK입니다.

## 특징

- 🔐 간단한 인증 플로우
- 📤 이미지 업로드 (로컬 파일, URL, 바이트)
- 🚀 토큰 생성 (API 서명 + 블록체인 실행)
- 💰 잔액 확인
- 🌐 멀티 네트워크 지원 (BSC, Arbitrum, Base)

## 설치

```bash
pip install -r requirements.txt
```

## 빠른 시작

```python
from meme_manager import MemeSDK, CreateTokenParams, TokenLabel

# SDK 초기화
sdk = MemeSDK(private_key="your_private_key", network="BSC")

# 인증
sdk.authenticate()

# 토큰 생성
params = CreateTokenParams(
    name="My Token",
    symbol="MTK",
    description="My awesome token",
    image_url="https://example.com/image.png",
    label=TokenLabel.MEME
)

result = sdk.create_token_with_image_upload(params)
print(f"Token created: {result['token_address']}")
```

## 주요 기능

### 1. 인증

```python
access_token = sdk.authenticate("MetaMask")
# 또는 기존 토큰 재사용
sdk.set_access_token(existing_token)
```

### 2. 이미지 업로드

```python
# 로컬 파일에서
url = sdk.upload_image("./image.png")

# URL에서
url = sdk.upload_image_from_url("https://example.com/image.png")

# 바이트에서
url = sdk.upload_image_from_bytes(image_bytes, "image.png")
```

### 3. 토큰 생성

```python
params = CreateTokenParams(
    name="Token Name",
    symbol="TKN",
    description="Token description",
    image_url="https://...",  # 또는 업로드된 URL
    label=TokenLabel.MEME,
    website="https://example.com",  # 선택사항
    twitter="https://x.com/...",    # 선택사항
    telegram="https://t.me/...",    # 선택사항
    presale_bnb="0"                 # 프리세일 BNB 양
)

result = sdk.create_token(params)
```

### 4. 잔액 확인

```python
balance = sdk.get_balance()
print(f"Balance: {balance['formatted']}")
```

## 텔레그램 봇에서 사용

```python
from meme_manager import MemeSDK, CreateTokenParams, TokenLabel

async def create_token_handler(update, context):
    # SDK 초기화
    sdk = MemeSDK(private_key=PRIVATE_KEY)

    try:
        # 인증
        sdk.authenticate()

        # 토큰 생성
        params = CreateTokenParams(
            name=user_input["name"],
            symbol=user_input["symbol"],
            description=user_input["description"],
            image_url=user_input["image_url"],
            label=TokenLabel.MEME
        )

        result = sdk.create_token_with_image_upload(params)

        await update.message.reply_text(
            f"✅ Token created!\n"
            f"Address: {result['token_address']}\n"
            f"TX: {result['transaction_hash']}"
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
```

## 환경 변수

`env.example`을 `.env`로 복사하고 설정:

```bash
PRIVATE_KEY=your_private_key_here
```

## 예제 실행

```bash
python example.py
```

## 주의사항

- Private key는 절대 코드에 하드코딩하지 마세요
- 토큰 생성에는 최소 0.01 BNB의 가스비가 필요합니다
- 이미지는 jpg, png, gif, bmp, webp 형식만 지원됩니다
- 대부분의 기술적 파라미터는 플랫폼에서 고정되어 있습니다

## 라이센스

MIT
