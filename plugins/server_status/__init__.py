from nonebot import get_driver, on_command
from nonebot.matcher import Matcher

from .data_source import cpu_status, disk_usage, memory_status


command = on_command("状态", aliases={"status"}, priority=5, block=True)


@command.handle()
async def server_status(matcher: Matcher):

    msg = f"CPU: {int(cpu_status())}%\nMemory: {int(memory_status())}%"
    await matcher.send(msg)
