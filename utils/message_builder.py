from nonebot.adapters.onebot.v11 import MessageSegment
from pathlib import Path


def image(img_name: str , img_path: str) -> MessageSegment:
    img = Path(img_path) / img_name
    return MessageSegment.image(f"file:///{img.absolute()}")

def at(id: int) -> MessageSegment:
    return MessageSegment.at(id)