import base64
import mimetypes
import os
from typing import Tuple

import requests


def is_url(s: str) -> bool:
    if not s:
        return False
    s = str(s).strip().lower()
    return s.startswith("http://") or s.startswith("https://")


def _guess_media_type_from_path(path: str) -> str:
    media_type, _ = mimetypes.guess_type(path)
    if media_type:
        return media_type
    return "image/jpeg"


def load_image_bytes(image_path_or_url: str, timeout_s: int = 30) -> Tuple[bytes, str]:
    image_ref = str(image_path_or_url).strip()
    if not image_ref:
        return b"", "image/jpeg"

    if is_url(image_ref):
        resp = requests.get(image_ref, timeout=timeout_s)
        resp.raise_for_status()
        media_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0].strip() or "image/jpeg"
        return resp.content, media_type

    if not os.path.exists(image_ref):
        raise FileNotFoundError(f"Image file not found: {image_ref}")

    media_type = _guess_media_type_from_path(image_ref)
    with open(image_ref, "rb") as f:
        return f.read(), media_type


def load_image_base64(image_path_or_url: str, timeout_s: int = 30) -> Tuple[str, str]:
    image_bytes, media_type = load_image_bytes(image_path_or_url=image_path_or_url, timeout_s=timeout_s)
    if not image_bytes:
        return "", media_type
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return b64, media_type

