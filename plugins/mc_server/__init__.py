from nonebot import on_command

from utils.config_util import ConfigManager
from utils.utils import get_json

status = on_command('mc_status')
players = on_command('players')

data = {
    "server_url": "",
    "uuid": "",
    "remote_uuid": "",
    "apikey": "",
    "key": "",
    "port": ""
}

conf = ConfigManager.register("mc_status", data)


async def get_players():
    headers = {
        "key": conf["key"]
    }
    uri = f'{conf["server_url"]}:{conf["port"]}/v1/players'
    print(uri)
    js: list = await get_json(uri, headers=headers)
    return js


@players.handle()
async def _():
    headers = {
        "key": conf["key"]
    }
    uri = f'{conf["server_url"]}:{conf["port"]}/v1/players'
    js: list = await get_json(uri, headers=headers)
    if not js:
        await status.send('エラー発生。\n可能是服务器已关闭或服务端连接异常~')
        return
    msg = f'当前在线：{len(js)}人'
    if js:
        for i in js:
            msg += f'\n- {i["displayName"]}'
    await players.send(msg)


@status.handle()
async def mc_server_status():
    headers = {
        "key": conf["key"]
    }
    url = f'{conf["server_url"]}:{conf["port"]}/v1/server'
    info = await get_json(url, headers=headers)
    if not info:
        await status.send('エラー発生。\n可能是服务器已关闭或服务端连接异常~')
        return

    version = info["version"]
    player_list = await get_players()
    health = info["health"]

    up_time = health["uptime"]
    d = int(up_time / (24 * 3600))
    h = int((up_time / 3600) % 24)
    m = int((up_time / 60) % 60)
    s = int(up_time % 60)
    mem_max = round(health["maxMemory"]/(1024**3), 2)
    mem_free = round(health["freeMemory"]/(1024**3), 2)

    msg = f'服务端版本：{version}' \
        f'\n当前在线人数：{len(player_list)}'\
        f'\n内存占用: {round(mem_max - mem_free,2)}/{mem_max}G ({round((1-mem_free / mem_max) * 100, 2)}%)'\
        f'\n已运行：{d}天{h}时{m}分{s}秒'\

    await status.send(msg)
