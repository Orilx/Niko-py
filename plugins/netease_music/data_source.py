import httpx

base_url = 'https://wyy.orilx.top'


async def search_song(name: str):
    '''
    返回搜索列表里第一首歌
    '''
    params = {'keywords': name, 'limit': 1}
    try:
        resp = httpx.get(base_url + '/search', params=params)
    except httpx.ConnectError:
        return 'e'
    else:
        if resp.status_code != 200:
            return 'e'
        if not resp.json()["result"]['songCount']:
            return None
        return resp.json()["result"]["songs"][0]["id"]


async def get_song_info(id: str):
    '''
    获取歌曲详情
    '''
    params = {'ids': id}
    try:
        resp = httpx.get(base_url + '/song/detail', params=params)
    except httpx.ConnectError:
        return None
    else:
        if resp.status_code != 200:
            return None
        return resp.json()
