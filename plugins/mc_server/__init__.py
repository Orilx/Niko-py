from nonebot import on_command
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from utils.utils import get_json
from utils.config_util import ConfigManager

status = on_command('status')

data = {
    "server_url": "",
    "uuid": "",
    "remote_uuid": "",
    "apikey": ""
}
conf = ConfigManager.register("mc_status", data)


@status.handle()
async def mc_server_status(matcher: Matcher):
    query = {
        "uuid": conf["uuid"],
        "remote_uuid": conf["remote_uuid"],
        "apikey": conf["apikey"],
    }
    headers = {
        "accept": "application/json"
    }
    js = await get_json(conf["server_url"], query, headers)
    msg = ''
    if not js:
        msg += 'エラー発生'
        await matcher.send(msg)

    data = js['data']

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

    await matcher.send(msg)
