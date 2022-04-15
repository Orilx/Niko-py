from nonebot import on_command
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from utils.utils import get_json
from utils.config_util import sub_config

status = on_command('status')

d = {
    "server_url": "",
    "uuid": "",
    "remote_uuid": "",
    "apikey": ""
}
conf = sub_config.register("mc_status", d)
print(conf)


@status.handle()
async def _(event: GroupMessageEvent):
    if event.group_id not in conf["group_id"]:
        await status.finish()

    query = {
        "uuid": conf["uuid"],
        "remote_uuid": conf["remote_uuid"],
        "apikey": conf["apikey"],
    }
    headers = {
        "accept": "application/json"
    }
    js = await get_json(conf["server_url"], query, headers)
    if not js:
        await status.finish('エラー発生')

    data = js['data']
    msg = ''

    if data["status"] == 0:
        msg += f'服务器当前状态：关闭\n上次启动时间：{data["config"]["lastDatetime"]}'

    elif data["status"] == 3:
        if data["info"]["version"]:
            time = int(data["processInfo"]["elapsed"]) / 1000
            d = int(time / (24 * 3600))
            h = int((time / 3600) % 24)
            m = int((time / 60) % 60)
            s = int(time % 60)
            msg += f'服务器名称：{data["config"]["nickname"]}\n当前状态：开启\n' \
                   f'启动时间：{data["config"]["lastDatetime"]}\n服务端版本：{data["info"]["version"]}\n' \
                   f'在线人数：{data["info"]["currentPlayers"]}/{data["info"]["maxPlayers"]}\n已运行：{d}天{h}时{m}分{s}秒'
        else:
            msg += '服务器正在启动...'

    await status.finish(msg)
