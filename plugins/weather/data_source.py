from utils.config_util import ConfigManager
from utils.utils import get_json

data = {
    "api_key": "",
}
conf = ConfigManager.register("qweather", data)
api_key = conf["api_key"]


class Weather:
    url_weather_api = "https://devapi.qweather.com/v7/weather/"
    url_geoapi = "https://geoapi.qweather.com/v2/city/lookup"
    apikey = api_key

    @classmethod
    async def get_city_id(cls, city_name):
        res = await get_json(
            url=cls.url_geoapi,
            params={"range": "cn", "location": city_name, "key": cls.apikey}
        )
        if res["code"] == "200":
            return res["location"][0]["id"]
        else:
            return -1

    @classmethod
    async def now(cls, city_name) -> dict:
        city_id = await cls.get_city_id(city_name)
        if city_id == -1:
            return city_id
        res = await get_json(
            url=cls.url_weather_api + "now",
            params={"location": city_id, "key": cls.apikey},
        )
        return res

    @classmethod
    async def daily(cls, city_name) -> dict:
        city_id = await cls.get_city_id(city_name)
        if city_id == -1:
            return city_id
        res = await get_json(
            url=cls.url_weather_api + "3d",
            params={"location": city_id, "key": cls.apikey},
        )
        return res
