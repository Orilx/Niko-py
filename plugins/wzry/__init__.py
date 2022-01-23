import json
from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot import on_message
from .data_source import hero_table


wzry = on_message(block=False, priority=8)


@wzry.handle()
async def wzry_(event: GroupMessageEvent):
    msg = event.get_message()
    data_s = ''
    for s in msg:
        if s.type == 'json':
            data_s = s.data['data']
    if not data_s:
        await wzry.finish()
    data = json.loads(data_s)

    if 'shareData' not in data['meta'] or data['meta']['shareData']['appid'] != '1104466820':
        await wzry.finish()
    else:
        data = data['meta']['shareData']

        hero_id = hero_table.get(data['extData']['heroid'])
        if not hero_id:
            hero_id = data['extData']['heroid']
        partition = data['roleInfo']['partition']
        partition = partition.replace('\\', '')
        role_name = data['roleInfo']['roleName']
        score = data['wzryRecordInfo']['score']
        is_mvp = '     MVP' if data['wzryRecordInfo']['scoreImg'] else ''
        record_info = f"{data['wzryRecordInfo']['winNum']}胜 / {data['wzryRecordInfo']['loseNum']}负"

        msg = f'{role_name}\n本局战绩：\n使用英雄：{hero_id}\n{partition}\n本局评分：{score}{is_mvp}'

        await wzry.finish(msg)
