from utils.utils import get_json

base_url = 'https://wyy.orilx.top'


async def search_song(name: str):
    """
    返回搜索列表里第一首歌
    """
    params = {'keywords': name, 'limit': 1}
    rep = await get_json(base_url + '/search', params=params)
    if not rep["result"]['songCount']:
        return None
    return rep["result"]["songs"][0]["id"]


async def get_song_info(id: str):
    """
    获取歌曲详情
    """
    params = {'ids': id}
    return get_json(base_url + '/song/detail', params=params)
