# Niko-py
基于Nonebot2开发的QQ机器人

## 已实现功能
- [x] 微博订阅
- [x] 基于 [强智教务API](https://github.com/WindrunnerMax/SHST) 的课表查询
- [x] 喜报图片生成
- [x] 伪造群员发言
- [x] 来点setu
- [x] 使用 [MCSManager](https://github.com/MCSManager/MCSManager) API 的 mc 服务器状态查询
- [x] 一言
- [x] bing每日一图
- [x] 天气查询（待完善）
- [x] 网易云音乐点歌（待完善）
- [x] ...


## 依赖库
```bash
pip install ruamel.yaml psutil gmqtt 
```

## 依赖插件
- nonebot-plugin-htmlrender 

```bash
nb plugin install nonebot-plugin-htmlrender
```

PS: 要简化配置流程，也可以考虑额外安装 [nonebot_plugin_gocqhttp](https://github.com/mnixry/nonebot-plugin-gocqhttp) 插件
```bash
nb plugin install nonebot-plugin-gocqhttp
```

## 感谢
[botuniverse / onebot](https://github.com/botuniverse/onebot) ：一个聊天机器人应用接口标准  
[Mrs4s / go-cqhttp](https://github.com/Mrs4s/go-cqhttp) ：cqhttp的golang实现，轻量、原生跨平台.  
[nonebot / nonebot2](https://github.com/nonebot/nonebot2) ：跨平台Python异步机器人框架  
[WindrunnerMax / SHST](https://github.com/WindrunnerMax/SHST) ：强智教务API & 山科小站  
[StarHeartHunt / WeiboMonitor](https://github.com/StarHeartHunt/WeiboMonitor) ：微博爬虫  
[HibiKier / zhenxun_bot](https://github.com/HibiKier/zhenxun_bot) ：绪山真寻Bot
[MinatoAquaCrews / nonebot_plugin_crazy_thursday](https://github.com/MinatoAquaCrews/nonebot_plugin_crazy_thursday) ：疯狂星期四

