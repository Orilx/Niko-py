from pathlib import Path

from nonebot import get_driver
from ruamel import yaml

super_group = get_driver().config.super_group


class Config:
    def __init__(self, path, data):
        # 如果文件不存在，就自动生成
        self.path = path
        if not path.is_file():
            with open(path, "w", encoding="utf-8") as f:
                f.write(yaml.dump(data, default_flow_style=False))
        self.source_data = yaml.load(path.read_bytes(), Loader=yaml.Loader)

    def save_file(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(yaml.dump(data, default_flow_style=False, allow_unicode=True,
                              Dumper=yaml.RoundTripDumper))
        return True


class ConfigFileManager(Config):
    """
    存储各个配置文件的文件名
    """

    def __init__(self):
        path = Path('data/config/config_files.yaml')
        self.path_dict = dict()
        super().__init__(path, self.path_dict)

    def add_path(self, file_name: str):
        self.path_dict[file_name] = f'{file_name}.yaml'
        super().save_file(self.path_dict)

    def get_paths(self):
        return self.source_data


# TODO 待修改，实例化 配置文件地址 存储类
file_manager = ConfigFileManager()


class SubConfig(Config):
    """
    TODO 待完善
    """

    def __init__(self, name: str):
        config_files = file_manager.get_paths()
        if name in config_files:
            path = Path(f"data/config/{config_files[name]}")
        else:
            file_manager.add_path(name + '_config')
            path = Path(f'data/config/{name}_config.yaml')
        super().__init__(path, {'group_id': super_group})

    def get_groups(self) -> list:
        return self.source_data['group_id']

    async def add_group(self, group_id: int) -> bool:
        if group_id in self.get_groups():
            return False
        self.source_data['group_id'].append(group_id)
        return super().save_file(self.source_data)

    async def rm_group(self, group_id: int) -> bool:
        if group_id not in self.get_groups():
            return False
        self.source_data['group_id'].remove(group_id)
        return super().save_file(self.source_data)

    def has_group(self, group_id: int) -> bool:
        return group_id in self.get_groups()
