import asyncio
from nonebot import get_driver
from utils.utils import get_json

api_key = get_driver().config.qweather_apikey


class Weather:
    def __url__(self):
        self.url_weather_api = "https://devapi.qweather.com/v7/weather/"
        self.url_geoapi = "https://geoapi.qweather.com/v2/city/lookup"

    def __init__(self, city_name: str):
        self.daily = None
        self.now = None
        self.city_id = None
        self.city_name = city_name
        self.apikey = api_key
        self.__url__()

    async def load_data(self):
        self.city_id = await self._get_city_id()
        self.now, self.daily = await asyncio.gather(
            self._now, self._daily
        )

    async def _get_city_id(self):
        res = await get_json(
            url=self.url_geoapi,
            params={"range": "cn", "location": self.city_name, "key": self.apikey}
        )
        if res["code"] == "200":
            return res["location"][0]["id"]
        else:
            return -1

    @property
    async def _now(self) -> dict:
        res = await get_json(
            url=self.url_weather_api + "now",
            params={"location": self.city_id, "key": self.apikey},
        )
        return res

    @property
    async def _daily(self) -> dict:
        res = await get_json(
            url=self.url_weather_api + "3d",
            params={"location": self.city_id, "key": self.apikey},
        )
        return res
