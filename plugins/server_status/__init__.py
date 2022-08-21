from nonebot import on_command, plugin
from nonebot.matcher import Matcher

from .data_source import cpu_status, disk_usage, memory_status

__plugin_meta__ = plugin.PluginMetadata(
    name='服务器状态',
    description='获取当前服务器状态',
    usage=f"""/状态  # 获取当前服务器状态"""
)

command = on_command("状态", aliases={"status"}, priority=5, block=True)


@command.handle()
async def server_status(matcher: Matcher):

    msg = f"CPU: {int(cpu_status())}%\nMemory: {int(memory_status())}%"
    await matcher.send(msg)
