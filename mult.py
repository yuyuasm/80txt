import requests as req
from bs4 import BeautifulSoup as bs
import logging as log
import re
from urllib.parse import urljoin
from pyquery import PyQuery as pq
from os import makedirs
from os.path import exists
import json
import multiprocessing as multip
import pymongo



log.basicConfig(level=log.INFO, format='%(asctime)s - %(levelname)s: %(message)s')


TOTAL_URL_ITEMS = ["https://txt80.cc/recommendall/index.html"] + [f"https://txt80.cc/recommendall/index_{i}.html" for i in range(2, 190)]
BASE_URL = 'https://www.txt80.cc/'

"""
with open("80.html", "w") as f:

    r = req.get("https://www.txt80.cc/dushi/txt26767.html")
    r.encoding = 'utf-8'
    str = r.text

    f.write(bs(str, 'lxml').prettify())
                 """


def scrapy_page(url):
    log.info(f'scraping {url}...')
    try:
        response = req.get(url)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            return response.text
        log.error(f'get invalid status code {response.status_code} while scraping {url}')
    except req.RequestException:
        log.error(f'error occurred while scraping {url}', exc_info=True)



def scrapy_index(page):
    return scrapy_page(page)


def parse_index(html):
    pattern = re.compile('<h4>.*?<a href="(.*?)" target="_blank">')
    items = re.findall(pattern, html)
    if not items:
        return []
    for it in items:
        detail_url = urljoin(BASE_URL, it)
        log.info(f'get detail url {detail_url}')
        yield detail_url


        #   <a href="/wuxia/txt49256.html" target="_blank">


def scrapy_detail(url):
    return scrapy_page(url)


def parse_detail(html):
    # <a href="http://www.txt80.cc/writer/剑沉黄海/" title="剑沉黄海">
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

RESULTS_DIR = 'results'
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)

def save_data(data):
    name = data.get('name')
    data_path = f'{RESULTS_DIR}/{name}.json'
    json.dump(data, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

"""
client = pymongo.MongoClient(host='localhost', username='adminl', password='admin123', port=27017)
db = client.txt80
collection = db.info

def save_data(data):
    collection.insert_one(data)

    """
    




def main(page):
    index_html = scrapy_index(page)
    detail_urls = parse_index(index_html)
    for detail_url in detail_urls:
        detail_html = scrapy_detail(detail_url)
        data = parse_detail(detail_html)
        log.info(f'get detail data {data}')
        log.info('saving data to json file')
        save_data(data)
        log.info('data saved successfully')


if __name__ == '__main__':
    pool = multip.Pool()
    pool.map(main, TOTAL_URL_ITEMS)
    pool.close()
    pool.join()


    

