from nonebot import on_command
from utils.utils import get_json

status = on_command('status')

server_url = 'https://mc.orilx.top/api/status/new_world'

@status.handle()
async def status_():
    
    js = await get_json(server_url)
    msg = ''
    if js['status']:
        if "lastDate" in js:
            msg += '服务器正在启动...'
        else:
            msg += f'服务器当前状态：开启\n服务器名称：{js["serverName"]}\n服务端版本：{js["version"]}\n在线人数：{js["current_players"]}/{js["max_players"]}'
        
    else:
        msg += f'服务器当前状态：关闭\n上次启动时间：{js["lastDate"]}'
    await status.finish(msg)