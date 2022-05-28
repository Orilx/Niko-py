from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment
from nonebot.params import CommandArg
from utils.message_builder import fake_forward_msg
from utils.utils import send_group_forward_msg

fake = on_command('fake', aliases={"假消息"}, priority=5, block=True)


@fake.handle()
async def _(event: GroupMessageEvent, args: Message = CommandArg()):
    at = []
    msg = []
    fake_msg = []

    for i in args:
        if i.type == 'at':
            if i.data["qq"] == 'all':
                continue
            else:
                at.append(i.data["qq"])
        else:
            msg.append(i)

    for i in msg:
        if i.type == 'text':
            if i.data["text"].strip():
                fake_msg.append(MessageSegment.text(i.data["text"].strip()))
        else:
            fake_msg.append(i)

    if at and fake_msg:
        group_forward_msg = await fake_forward_msg(at, event.group_id, fake_msg)
        await send_group_forward_msg(event.group_id, group_forward_msg)
    else:
        await fake.finish("参数有误~")
