import os
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from google import genai


def edit_images_bytes(
    prompt: str,
    image1_bytes: bytes,
    image2_bytes: bytes,
) -> bytes:

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    img1 = Image.open(BytesIO(image1_bytes))
    img2 = Image.open(BytesIO(image2_bytes))

    resp = client.models.generate_content(
        model="gemini-2.5-flash-image-preview",
        contents=[prompt, img1, img2],
    )

    for cand in getattr(resp, "candidates", []) or []:
        for part in getattr(cand, "content", {}).parts or []:
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                return inline.data

    raise RuntimeError("No image data returned from Gemini response")
