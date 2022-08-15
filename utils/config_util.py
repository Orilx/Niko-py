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
                f.write(yaml.dump(data, default_flow_style=False, allow_unicode=True,
                                  Dumper=yaml.RoundTripDumper))
        self.source_data = yaml.load(path.read_bytes(), Loader=yaml.Loader)

    def save_file(self):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(yaml.dump(self.source_data, default_flow_style=False, allow_unicode=True,
                              Dumper=yaml.RoundTripDumper))


# 解决Python写入yaml后排版混乱还丢失注释问题
# def setDictYaml(self, fileDir, fileName, key, value):
#     with open(filePath(fileDir, fileName), 'r', encoding="utf-8") as f:
#         doc = yaml.round_trip_load(f)
#     doc[key] = value
#     with open(filePath(fileDir, fileName), 'w', encoding="utf-8") as f:
#         yaml.round_trip_dump(doc, f, default_flow_style=False)
# setDictYaml(fileDir='config', fileName='config.yaml', key='password', value=123)

class ConfigManager:
    """
    bot 配置文件管理类
    """
    path = Path("data/config/bot_config.yaml")
    file_manager = FileManager(path, {})
    data = file_manager.source_data

    @classmethod
    def register(cls, code: str, data: dict = None):
        """
        在 bot_config.yaml 中注册项目
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
    bot 订阅文件管理类
    """
    path = Path("data/bot_sub_list.yaml")
    file_manager = FileManager(path, {})
    data = file_manager.source_data

    @classmethod
    def register(cls, code: str, data: dict = None):
        """
        在 bot_config.yaml 中注册项目
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


class SubItem:
    """
    bot 订阅相关管理类
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
        self.data = SubManager.register(code, d)

    async def save_file(self):
        SubManager.save(self.code, self.data)
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
    def get(cls, name) -> SubItem:
        return cls.items.get(name)

    @classmethod
    def add(cls, name: str, sub: SubItem) -> SubItem:
        cls.items[name] = sub
        logger.info(f"订阅添加: {name}")
        return sub


def add_sub_config(name: str, code: str) -> SubItem:
    return SubList.add(name, SubItem(code))
