import io
import os, json

from src.utils.r2.client import client

BUCKET = os.environ["R2_BUCKET"]
R2_ENDPOINT = os.environ["R2_ENDPOINT"]
CUSTOM_DOMAIN = os.environ["CUSTOM_DOMAIN"]

r2 = client()


def get_r2_url(key: str) -> str:
    return f"{CUSTOM_DOMAIN}/{key}"


def upload_image(data: bytes, file_name: str) -> str:
    key = f"images/{file_name}.jpg"
    buf = io.BytesIO(data)
    buf.seek(0)

    r2.upload_fileobj(buf, BUCKET, key, ExtraArgs={"ContentType": "image/jpeg"})
    return get_r2_url(key)


def upload_json(data: dict, file_name: str) -> str:
    key = f"metadatas/{file_name}.json"
    body = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    buf = io.BytesIO(body)
    buf.seek(0)

    r2.upload_fileobj(
        buf, BUCKET, key, ExtraArgs={"ContentType": "application/json; charset=utf-8"}
    )

    return get_r2_url(key)
