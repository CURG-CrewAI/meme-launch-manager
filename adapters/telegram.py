import json
import asyncio, queue
from typing import Any, Dict, List, Optional
from telegram.constants import ChatAction
import io


class TelegramAdapter:
    def __init__(self, app, chat_id: int, loop: asyncio.AbstractEventLoop):
        self.app = app
        self.chat_id = chat_id
        self.loop = loop
        self.q: "queue.Queue[str]" = queue.Queue()

    def _submit(self, coro):
        asyncio.run_coroutine_threadsafe(coro, self.loop)

    def _load_file_bytes(self, file_id: str) -> bytes:
        async def _do():
            file = await self.app.bot.get_file(file_id)
            bytesIO = io.BytesIO()
            await file.download_to_memory(out=bytesIO)
            return bytesIO.getvalue()

        future = asyncio.run_coroutine_threadsafe(_do(), self.loop)
        return future.result()

    def put_answer(self, text: str):
        self.q.put(text or "")

    # Send
    def send(self, text: str):
        if text is None:
            text = ""
        self._submit(self.app.bot.send_message(self.chat_id, text))

    def send_trends(self, trends: List[dict]):
        lines = ["📢 Top trending keywords with reasons:\n"]
        for idx, item in enumerate(trends, start=1):
            keyword = item.get("keyword") or "N/A"
            reason = item.get("why_trending") or "No explanation available."
            lines.append(f"{idx}. {keyword} — {reason}\n")
        self.send("\n".join(lines))

    def send_photo(self, data: bytes, filename: str, caption: str = ""):
        bytesIO = io.BytesIO(data)
        bytesIO.name = filename
        self._submit(
            self.app.bot.send_document(
                self.chat_id, document=bytesIO, caption=caption or ""
            )
        )

    def send_json(self, path: str, indent: int = 2):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            text = json.dumps(data, ensure_ascii=False, indent=indent)
            self.send(text)
        except Exception as e:
            self.send(f"[JSON File Error] {e!r}")

    # Get
    def _get(self, prompt: str) -> str:
        self.send(prompt)
        try:
            return self.q.get(timeout=300)
        except queue.Empty:
            self.send("Timeout. Ending the flow.")
            raise TimeoutError("user input timeout")

    def get_trend_choice(self, trends: list[dict], default: int = 1) -> Optional[dict]:
        selected_number = default
        answer = self._get(
            f"\nChoose the trend keyword number you want (default={default})"
        )
        if not answer:
            self.send(f"Invalid input (empty). Default ({default}) selected.")
        elif not answer.strip().isdigit():
            self.send(f"Invalid input (not a number). Default ({default}) selected.")
        else:
            number = int(answer.strip())
            if 1 <= number <= len(trends):
                selected_number = number
            else:
                self.send(f"Invalid range. Default ({default}) selected.")

        selected_trend = trends[selected_number - 1] or []
        self.send(f"\n✅ Selected keyword: {(selected_trend.get('keyword') or 'N/A')}")
        return selected_trend

    def get_confirmation(
        self, prompt: str = "Proceed? (Y/N)", default: bool = False
    ) -> bool:
        answer = (self._get(prompt) or "").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        return default

    def get_text(self, prompt: str = "Enter answer") -> Optional[str]:
        answer = (self._get(prompt) or "").strip()
        return answer or None

    def get_image(self, prompt: str = "Enter answer") -> Optional[bytes]:
        while True:
            image = self._get(prompt)
            if image.get("type") == "photo":
                break
            self.send(f"A photo is required. Please try again")
        return self._load_file_bytes(image["file_id"])
