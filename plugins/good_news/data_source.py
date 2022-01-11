import asyncio
from playwright.async_api import async_playwright
from pathlib import Path

PATH = Path('resources/html/xibao.html').absolute()

async def get_img(text: str):
    len_chi = 10
    len_eng = 2 * len_chi
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        page = await browser.new_page()
        await page.set_viewport_size({"width": 600, "height": 430})
        await page.goto(f"file://{PATH}?text={text}")
        img = await page.screenshot()  #截图
        await browser.close()
        return img
