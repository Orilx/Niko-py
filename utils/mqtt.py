from gmqtt import Client
from nonebot.log import logger
from utils.config_util import ConfigManager

data = {
    "host": "114.51.41.91",
    "port": 11451,
    "user": "user",
    "password": "password"
}

conf_data = ConfigManager.register("mqtt", data)


class MQTTClient:
    def __init__(self, conf, client_id, **kwargs):
        self.port = conf["port"]
        self.host = conf["host"]
        self.client_id = client_id
        self.client = Client(client_id)
        self.client.set_auth_credentials(conf["user"], conf["password"])

        # asyncio.ensure_future(self.connect())
        self.client.on_connect = kwargs.pop('on_connect', self.on_connect)
        self.client.on_message = kwargs.pop('on_message', self.on_message)
        self.client.on_disconnect = kwargs.pop('on_disconnect', self.on_disconnect)
        self.client.on_subscribe = kwargs.pop('on_subscribe', self.on_subscribe)

    async def connect(self):
        await self.client.connect(self.host, self.port)

    async def disconnect(self):
        await self.client.disconnect()

    def on_connect(self, client, flags, rc, properties):
        logger.info(f"Mqtt client [{self.client_id}] connected.")

    def on_message(self, client, topic, payload, qos, properties):
        msg = f"Mqtt client [{self.client_id}] topic:[{topic}] receive msg {payload.decode('utf-8')}"
        logger.info(msg)

    def on_disconnect(self, client, packet, exc=None):
        logger.info(f'Mqtt client [{self.client_id}] disconnected.')

    def on_subscribe(self, client, mid, qos, properties):
        # logger.info(f'Mqtt topic [{self.topic}] subscribed.')
        logger.info(f'Mqtt topic subscribed.')


async def create_connection(client_id, **kwargs):
    client = MQTTClient(conf_data, client_id, **kwargs)
    # 确保建立连接之后再返回client实例
    await client.connect()
    return client


async def conn_and_subscribe(client_id, **kwargs):
    client = MQTTClient(conf_data, client_id, **kwargs)
    return client
