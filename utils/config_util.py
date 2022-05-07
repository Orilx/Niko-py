from pathlib import Path
from typing import Union

from nonebot import get_driver, logger
from ruamel import yaml

super_group = get_driver().config.super_group


class FileManager:
    def __init__(self, path, data: Union[dict, list]):
        # 如果文件不存在，就自动生成
        self.path = path
        if not path.is_file():
            with open(path, "w", encoding="utf-8") as f:
                f.write(yaml.dump(data, default_flow_style=False))
        self.source_data = yaml.load(path.read_bytes(), Loader=yaml.Loader)

    def save_file(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(yaml.dump(self.source_data, default_flow_style=False, allow_unicode=True,
                              Dumper=yaml.RoundTripDumper))


class ConfigManager:
    """
    bot 配置文件管理类
    """
    path = Path(f"data/config/bot_configs.yaml")
    file_manager = FileManager(path, {})
    data = file_manager.source_data

    @classmethod
    def register(cls, code: str, data: dict = None):
        """
        在 bot_configs.yaml 中注册订阅项目，手动定义额外字段
        """
        if code in cls.data:
            return cls.data[code]

        cls.save(code, data)
        return cls.data[code]

    @classmethod
    def save(cls, code, data):
        cls.data[code] = data
        cls.file_manager.source_data = cls.data
        cls.file_manager.save_file()


class SubManager:
    """
    bot订阅相关配置管理类
    TODO 应该有更好的解决方案
    """

    def __init__(self, code: str, data: dict = None):
        self.code = code
        d = {
            "group_id": [int(i) for i in super_group],
            "enable": True
        }
        if data:
            for k, v in data.items():
                d[k] = v
        self.data = ConfigManager.register(code, d)

    async def save_file(self):
        ConfigManager.save(self.code, self.data)
        return True

    def get(self, param: str = None):
        return self.data.get(param)

    def get_data(self):
        return self.data

    def get_groups(self) -> list:
        return self.data["group_id"]

    async def add_group(self, group_id: int) -> bool:
        if group_id in self.get_groups():
            return False
        self.data["group_id"].append(group_id)
        return await self.save_file()

    async def rm_group(self, group_id: int) -> bool:
        if group_id not in self.get_groups():
            return False
        self.data["group_id"].remove(group_id)
        return await self.save_file()

    def get_status(self) -> bool:
        return self.data["enable"]

    async def ch_status(self) -> bool:
        """
        改变启用状态
        """
        self.data["enable"] = not self.get_status()
        await self.save_file()
        return self.get_status()

    def has_group(self, group_id: int) -> bool:
        return group_id in self.get_groups()


class SubList:
    """
    给 订阅管理 设计的数据类
    """
    items = {}

    @classmethod
    def get_items(cls):
        return cls.items

    @classmethod
    def get(cls, name) -> SubManager:
        return cls.items.get(name)

    @classmethod
    def add(cls, name: str, sub: SubManager) -> SubManager:
        cls.items[name] = sub
        logger.info(f"订阅添加: {name}")
        return sub
