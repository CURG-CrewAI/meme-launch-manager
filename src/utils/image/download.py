import os


def download_image(image_bytes: bytes, folder_path: str, filename: str):

    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path, filename)

    with open(file_path, "wb") as f:
        f.write(image_bytes)

    print(f"Save Image!!: {file_path}")
