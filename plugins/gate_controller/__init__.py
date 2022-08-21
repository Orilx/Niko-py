import json
from asyncio import sleep

from nonebot import on_command, plugin, get_driver
from nonebot.adapters.onebot.v11 import GroupMessageEvent

from utils.cq_utils import send_group_msg
from utils.mqtt import create_connection

__plugin_meta__ = plugin.PluginMetadata(
    name='门禁',
    description='门禁相关指令',
    usage=f"""/get_temp  # 获取当前室内温湿度""",
)

driver = get_driver()


get_temp = on_command('get_temp', priority=5, block=True)


@get_temp.handle()
async def _(event: GroupMessageEvent):
    group_id = event.group_id
    qid = event.user_id

    async def on_msg_callback(client, topic, payload, qos, properties):
        data = json.loads(payload.decode('utf-8'))
        m = f'temp: {data["temp"]}℃\nhumi: {data["humi"]}%\nbatt: {data["batt"]}%\ntime: {data["time"]}'
        if data["batt"] == -1:
            m = data["remark"]
        await send_group_msg(group_id, m)
        await client.disconnect()

    def on_conn_callback(client, flags, rc, properties):
        client.publish('test/mi_sensor', {'flag': 1})

    temp = await create_connection(f'{group_id}_{qid}', on_message=on_msg_callback, on_connect=on_conn_callback)
    temp.client.subscribe('test/temp')

    await get_temp.send('正在获取传感器信息...')
    await sleep(15)
    if temp.client.is_connected:
        await temp.disconnect()
        await get_temp.send('获取数据超时，请稍后再试！')
