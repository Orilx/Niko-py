# Niko-py

基于 [Nonebot2](https://github.com/nonebot/nonebot2) 开发的QQ机器人

## 已实现功能

*未打勾的功能有待完善  ~~咕咕~~*

- [x] 一言
- [x] 来点setu
- [x] 微博订阅
- [x] 天气查询
- [x] 伪造群员发言
- [x] 获取 bing 每日一图
- [x] 基于 [强智教务API](https://github.com/WindrunnerMax/SHST) 的课表查询
- [x] 使用 [ServerTap](https://github.com/phybros/servertap) API 的 mc 服务器状态查询
- [x] 帮助文档
- [ ] 网易云音乐点歌
- [ ] 喜报图片生成
- [ ] ~~青岛卫健委疫情信息推送~~ 已经结束力
- [ ] ...

## 部署

### 使用 pdm（推荐）

- 确保你的系统中安装了Python3.10 和 [pdm](https://pdm.fming.dev/latest/)
- 拉取本仓库
- 在仓库文件所在的目录下执行如下指令
  ```bash
  pdm install
  ```
- 待指令执行完毕后，使用 `nb run` 来启动 Niko-py

### 直接部署

- 确保你的系统里安装了 Python3.10
- 拉取本仓库
- 切换到仓库文件所在的文件夹中
- 安装依赖库
  ```bash
  pip install nb-cli ruamel.yaml psutil gmqtt slowapi lxml nonebot-adapter-onebot nonebot_plugin_apscheduler nonebot-plugin-htmlrender
  ```

**PS**

要简化配置流程，也可以考虑额外安装 [nonebot_plugin_gocqhttp](https://github.com/mnixry/nonebot-plugin-gocqhttp) 插件

```bash
nb plugin install nonebot-plugin-gocqhttp
```

具体配置方式参考其文档

## 配置

Niko-py 部署完成后需要启动一次来生成配置文件

使用 `nb run` 命令启动， 待启动完成后按下 `Ctrl+C` 停止

**第一次启动后的文件夹结构如下所示（为简化视图，仅展示部分重要文件）**

```
Niko-py
|   .env.prod               # 基础配置文件
|   bot.py                  # 程序入口
|   pyproject.toml          # 用于安装依赖程序
|   README.md               # 本文档
|
+---cache
|
+---data
|   |   bot_sub_list.yaml   # bot 订阅管理插件使用，一般情况下无需改动
|   |   cs_main_data.yaml   # 当配置好 'cs_config' 后，每周末 bot 会将下周的课程表同步到此文件中
|   |   wb_sub_list.yaml    # 微博订阅插件使用
|   |
|   \---config
|           bot_config.yaml # bot 配置文件
|           cs_config.yaml  # 课程表插件所使用的配置文件
|
+---plugins                 # 插件存放目录
|
+---resources
|
+---services
|
\---utils
```

下面是各个配置文件的内容,修改请参照注释
<details>  
<summary>点击展开</summary>  

### conf.prod

基础配置文件(仅在初次部署时修改)

```env
HOST=127.0.0.1
PORT=8080
SUPERUSERS=["123456789"]  # 配置 NoneBot 超级用户
NICKNAME=["Niko"]  # 配置机器人的昵称
COMMAND_START=["/", ""]  # 配置命令起始字符
COMMAND_SEP=["."]  # 配置命令分割字符

SUPER_GROUP=["123456789"] # 测试用群组
```

### bot_config.yaml

bot 配置文件(随着 bot 升级，内容可能有所变化)

```yaml
mqtt: # mqtt 相关配置项
  host: 127.0.0.1    # broker 的 IP
  port: 11451
  user: user
  password: password
mc_status:
  server_url: 127.0.0.1  # MC 服务器 IP (需要安装 ServerTap)
  key: example.key
  port: 25576
qweather:
  api_key: EXAMPLE_KEY      # 和风天气 api_key
```

### cs_config.yaml

课程表插件配置文件

该插件仅适配了`山东科技大学强智教务系统`

```yaml
userInfo: # 强智系统的用户名和密码
  account: 'account'
  password: 'password'
super_group: # 订阅每日课表提醒的群组
  - 123456789
start_date: '2021-06-23'    # 开学日期
location: 黄岛        # 用于获取当日天气，每天课表提醒时使用
enable: false
```

</details>

## 感谢

[botuniverse / onebot](https://github.com/botuniverse/onebot) ：一个聊天机器人应用接口标准  
[Mrs4s / go-cqhttp](https://github.com/Mrs4s/go-cqhttp) ：cqhttp的golang实现，轻量、原生跨平台  
[nonebot / nonebot2](https://github.com/nonebot/nonebot2) ：跨平台Python异步机器人框架  
[WindrunnerMax / SHST](https://github.com/WindrunnerMax/SHST) ：强智教务API & 山科小站  
[felinae98 / nonebot-bison](https://github.com/felinae98/nonebot-bison) ：Bison 通用订阅推送插件
[HibiKier / zhenxun_bot](https://github.com/HibiKier/zhenxun_bot) ：绪山真寻Bot  

