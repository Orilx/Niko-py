import re
import json
import nonebot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot import on_message


repeater = on_message(block=False, priority=10)

msg_cache = dict()
repeated_message = dict()


@repeater.handle()
async def repeater_(event: GroupMessageEvent):

    if event.is_tome():
        return

    group_id = event.group_id
    msg = event.get_message()
    raw_msg = event.raw_message
    
    if raw_msg[0] == '/':
        await repeater.finish()
    
    if group_id not in msg_cache.keys():
        msg_cache[group_id] = raw_msg
        repeated_message[group_id] = None
        return

    urls = [
        s.data['url']
        for s in msg
        if s.type == 'image' and 'url' in s.data
    ]
    
    if urls:
        if(len(urls) > 1):
            await repeater.finish()
        r_msg = re.split(r'\[.*\]',event.raw_message)
        msg = MessageSegment.text(r_msg[0]) + MessageSegment.image(urls[0]) + r_msg [1]

    if msg_cache[group_id] == raw_msg and repeated_message[group_id] != raw_msg:
        repeated_message[group_id] = raw_msg
        await repeater.finish(msg)
    else:
        msg_cache[group_id] = raw_msg
