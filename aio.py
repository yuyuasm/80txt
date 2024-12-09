import logging as log
import asyncio as asyn
import aiohttp as aio
import re
from urllib.parse import urljoin
from os import makedirs
from os.path import exists
import json
from pyquery import PyQuery as pq


log.basicConfig(level=log.INFO, format="%(asctime)s - %(levelname)s: %(message)s")

TOTAL_URL_ITEMS = ["https://txt80.cc/recommendall/index.html"] + [f"https://txt80.cc/recommendall/index_{i}.html" for i in range(2, 190)]
BASE_URL = 'https://www.txt80.cc/'


async def scrapy_page(url):
    # 协程爬取数据
    log.info(f"scrapy {url}...")
    session = aio.ClientSession()
    response = await session.get(url)
    await response.text()
    await session.close()
    return response


async def scrapy_index(page):
    html = await scrapy_page(page)
    return html


def parse_index(html): 
    # 解析爬取主页 
    pattern = re.compile('<h4>.*?<a href="(.*?)" target="_blank">')
    items = re.findall(pattern, html)
    if not itmes:
        return []
    for it in items:
        detail_url = urljoin(BASE_URL, it)
        log.info(f'get detail url {detail_url}')
        yield detail_url


async def scrapy_detail(url):
    html = await scrapy_page(url)
    return html


def parse_detail(html):
    doc = pq(html)
    name = doc('.bt h2').text()
    writer = doc('.tuijian_title_txt a').text()
    box = doc('.cont').text().replace('ad2502()\n', '')
    box = re.sub(r'声明：全集TXT小说.*侵权的作品。', '', box, flags=re.DOTALL)
    return {
            'name': name,
            'writer': writer,
            'box': box,
            }
    """

    return {
            'name': "name",
            'writer': "writer",
            'box': "box",
            }
"""


RESULTS_DIR = "results"
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)


"""
def save_json(data):
    name = data.get('name')
    path_name = f'{RESULTS_DIR}/{name}.json'
    json.dump(data, open(path_name, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
"""


async def main(page):
    index_html = await scrapy_index(page)
    print("index_html", index_html.text)
    detail_urls = parse_detail(page)
    print(detail_urls)
    """
    for detail_url in detail_urls:
        detail_html = await scrapy_detail(detail_url)
        data = parse_detail(detail_html)
        log.info(f'get detail data {data}')
        log.info(f'save data to {RESULTS_DIR}/{data}.json file')
        save_json(data)
    """

if __name__ == '__main__':
    tasks = [asyn.ensure_future(main(page)) for page in TOTAL_URL_ITEMS]
    loop = asyn.get_event_loop()
    loop.run_until_complete(asyn.wait(tasks))

