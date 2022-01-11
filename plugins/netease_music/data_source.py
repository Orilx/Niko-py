import httpx

base_url = 'https://wyy.orilx.top'


async def search_song(name: str):
    '''
    返回搜索列表里第一首歌
    '''
    params = {'keywords': name, 'limit': 1}
    resp = httpx.get(base_url + '/search', params=params)
    if resp.status_code != 200:
        return None
    if not resp.json()["result"]['songCount']:
        return None
    return resp.json()["result"]["songs"][0]["id"]


async def get_song_info(id: int):
    '''
    获取歌曲详情
    '''
    params = {'ids': id}
    resp = httpx.get(base_url + '/song/detail', params=params)
    if resp.status_code != 200:
        return None
    return resp.json()
