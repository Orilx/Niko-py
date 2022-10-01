import json
from asyncio import sleep

from nonebot import on_command, plugin, get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from utils.cq_utils import send_group_msg
from utils.mqtt import create_connection

__plugin_meta__ = plugin.PluginMetadata(
    name='门禁',
    description='门禁相关指令',
    usage=f"""/get_temp  # 获取当前室内温湿度
/芝麻开门  # 发送开门指令""",
)

driver = get_driver()
super_group = driver.config.super_group

@driver.on_bot_connect
async def _():
    async def on_msg_callback(client, topic, payload, qos, properties):
        await filter(topic, payload)
        
    def decode(topic:str):
        li = topic.split('/')
        return li[-1] 
    
    async def filter(topic, payload):
        data = json.loads(payload.decode('utf-8'))
        if decode(topic) == 'online' or decode(topic) == 'offline':
            for i in super_group:
                await send_group_msg(i, data["msg"])
        return 'sub' in topic
    
    client = await create_connection('BOT_GLOBAL_CLIENT_001', on_message=on_msg_callback)
    client.client.subscribe('test/#')

from nonebot.permission import SUPERUSER

get_temp = on_command('get_temp', priority=5, block=True)
open_door = on_command('芝麻开门', priority=5, block=True, permission=SUPERUSER)

@get_temp.handle()
async def _(event: GroupMessageEvent):
    group_id = event.group_id
    qid = event.user_id

    async def on_msg_callback(client, topic, payload, qos, properties):
        data = json.loads(payload.decode('utf-8'))
        m = f'当前温度: {data["temp"]}℃\n当前湿度: {data["humi"]}%\n剩余电量: {data["batt"]}%\n获取时间: {data["time"]}'
        if data["batt"] == -1:
            m = data["remark"]
        await send_group_msg(group_id, m)
        await client.disconnect()

    def on_conn_callback(client, flags, rc, properties):
        client.publish('test/esp32/sub/gate/scan_mi_sensor', {'flag': 1})

    temp = await create_connection(f'{group_id}_{qid}', on_message=on_msg_callback, on_connect=on_conn_callback)
    temp.client.subscribe('test/esp32/gate/mi_sensor')

    await get_temp.send('正在获取传感器信息...')
    await sleep(15)
    if temp.client.is_connected:
        await temp.disconnect()
        await get_temp.send('获取数据超时，请稍后再试！')


@open_door.handle()
async def _(event: GroupMessageEvent):
    group_id = event.group_id
    qid = event.user_id
    
    async def on_msg_callback(client, topic, payload, qos, properties):
        data = json.loads(payload.decode('utf-8'))
        await send_group_msg(group_id, data["msg"])
        await client.disconnect()

    def on_conn_callback(client, flags, rc, properties):
        client.publish('test/esp32/sub/gate/open', {'flag': 1})
        
    tem = await create_connection(f'{group_id}_{qid}', on_message=on_msg_callback, on_connect=on_conn_callback)
    tem.client.subscribe('test/esp32/gate')
    await open_door.send('请求发送成功.')
    await sleep(10)
    if tem.client.is_connected:
        await tem.disconnect()
        await open_door.send('响应超时，设备可能离线！')