from pathlib import Path
from typing import Union

from nonebot import get_driver, logger
from ruamel import yaml

super_group = get_driver().config.super_group


class Config:
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
        return True


# class ConfigFileManager(Config):
#     """
#     存储各个配置文件的文件名
#     """
#
#     def __init__(self):
#         path = Path('data/config/config_files.yaml')
#         super().__init__(path, {})
#
#     def add_path(self, file_name: str):
#         self.source_data[file_name] = f'{file_name}.yaml'
#         super().save_file()
#
#     def get_paths(self):
#         return self.source_data


# 实例化 配置文件地址 存储类
# file_manager = ConfigFileManager()

class SubConfig(Config):
    """
    bot订阅相关配置文件管理类
    """

    def __init__(self):
        self.items = {}
        path = Path(f"data/config/bot_configs.yaml")
        super().__init__(path, {})

    def register(self, code: str, data: dict = None):
        """
        在 bot_configs 中注册订阅项目，可手动定义额外字段
        """
        if code in self.source_data:
            return self.source_data[code]

        d = {
            "group_id": [int(i) for i in super_group],
            "enable": True
        }
        if data:
            for k, v in data:
                d[code][k] = v

        self.source_data[code] = d
        self.save_file()
        return d

    async def save(self, name, data):
        self.source_data[name] = data
        super().save_file()


sub_config = SubConfig()


class SubManager:
    """
    bot订阅相关配置管理类
    TODO 应该有更好的解决方案
    """

    def __init__(self, code: str, data: dict = None):
        self.code = code
        self.data = sub_config.register(code, data)

    async def save_file(self):
        sub_config.source_data[self.code] = self.data
        await sub_config.save(self.code, self.data)
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

    def __init__(self):
        self.items = {}

    def get_items(self):
        return self.items

    def get(self, name):
        return self.items.get(name)

    def add(self, name: str, sub):
        self.items[name] = sub
        logger.info(f"订阅添加: {name}")
        return sub


sub_list = SubList()
