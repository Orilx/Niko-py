from ruamel import yaml
from pathlib import Path


class Config():
    def __init__(self, path, data=dict()):
        # 如果文件不存在，就自动生成
        self.path = path
        if not path.is_file():
            with open(path, "w", encoding="utf-8") as f:
                f.write(yaml.dump(data, default_flow_style=False))
        self.source_data = yaml.load(path.read_bytes(), Loader=yaml.Loader)

    def save_file(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(yaml.dump(data, default_flow_style=False,
                    Dumper=yaml.RoundTripDumper))
        return True


class ConfigFiles(Config):
    '''
    存储各个配置文件的文件名
    '''
    def __init__(self):
        path = Path('data/configs/config_files.yaml')
        defalt_paths = {
            'course_sub': 'course_sub_config.yaml',
            'honor_sub': 'honor_sub_config.yaml'
        }
        super().__init__(path, defalt_paths)

    def get_paths(self):
        return self.source_data


# TODO 待修改，实例化 配置文件地址 存储类
config_files = ConfigFiles().get_paths()

class SubConfig(Config):
    '''
    TODO 待完善
    '''
    def __init__(self, name: str):
        path = Path(f"data/configs/{config_files[name]}")
        super().__init__(path, {'group_id': [123456789]})

    def get_groups(self) -> list:
        return self.source_data['group_id']

    def add_group(self, group_id: int) -> bool:
        if group_id in self.get_groups():
            return False
        self.source_data['group_id'].append(group_id)
        return super().save_file(self.source_data)
        
    def rm_group(self, group_id: int) -> bool:
        if group_id not in self.get_groups():
            return False
        self.source_data['group_id'].remove(group_id)
        return super().save_file(self.source_data)
    
    def has_group(self, group_id: int) -> bool:
        return group_id in self.get_groups()

honor_sub_config = SubConfig('honor_sub')
course_sub_config = SubConfig('course_sub')


# class CourseSubConfig(Config):
#     '''
#     存储订阅每日课程表提醒的QQ群
#     初次初始化后需修改配置文件
#     TODO 待完善
#     '''

#     def __init__(self):
#         path = Path(f"data/configs/{config_files['course_sub']}")
#         super().__init__(path, {'group_id': [123456789]})

#     def get_groups(self) -> list:
#         return self.source_data['group_id']

#     def add_group(self, group_id: int) -> bool:
#         if group_id in self.get_groups():
#             return False
#         self.source_data['group_id'].append(group_id)
#         return super().save_file(self.source_data)
        
#     def rm_group(self, group_id: int) -> bool:
#         if group_id not in self.get_groups():
#             return False
#         self.source_data['group_id'].remove(group_id)
#         return super().save_file(self.source_data)

