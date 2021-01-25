#!/usr/bin/env python
# encoding: utf-8
"""
File Description: 抓取百度搜索的结果
Author: nghuyong
Mail: nghuyong@163.com
Created Time: 2019-09-26 16:56
"""
import json
import time
from multiprocessing import Pool
from pprint import pprint
import logging
import jieba
import requests
from lxml import etree

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

headers = {
    #"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36"
    #'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}


def crawl_baidu_search(keyword, num=5):

    url = "https://www.baidu.com/s?wd=" + keyword
    response = requests.get(url, headers=headers)
    content_tree = etree.HTML(response.text)

    # 取前三个搜索结果
    search_data = []
    search_results = content_tree.xpath('//div[@class="result c-container new-pmd"]')[:10]
    for index, search_result in enumerate(search_results, 1):
        time.sleep(0.5)
        try:
            abstract = search_result.xpath('.//div[@class="c-abstract"]')[0]
            abstract = abstract.xpath('string(.)')
            source = search_result.xpath('.//a[@data-click]')[0]
            source_link = source.xpath('./@href')[0]
            logger.info(source_link)
            title = source.xpath('string(.)')
            baidu_cache_link = search_result.xpath('.//a[text()="百度快照"]/@href')[0] + "&fast=y"
            search_data.append(
                {
                    'question_id': index,
                    'question': keyword,
                    'title': title,
                    'abstract': abstract,
                    'source_link': source_link,
                    'baidu_cache_link': baidu_cache_link
                }
            )
            if len(search_data) == num:
                break
        except:
            pass
    return search_data


def crawl_baidu_cache_page(url):
    response = requests.get(url, headers=headers)
    response.encoding = 'gbk'
    content_tree = etree.HTML(response.text)
    try:
        raw_content = content_tree.xpath('//div[@style="position:relative"]')[0]
    except:
        return ""
    raw_content = raw_content.xpath('string(.)')
    valid_lines = []
    for line in raw_content.split('\n'):
        line = line.strip()
        if line:
            valid_lines.append(line)
    valid_content = "。".join(valid_lines)
    return valid_content


def crawl(keyword):
    search_data = crawl_baidu_search(keyword)
    results = []
    pool = Pool(processes=3)
    for each_search_data in search_data:
        results.append(pool.apply_async(crawl_baidu_cache_page, args=(each_search_data['baidu_cache_link'],)))
    pool.close()
    pool.join()
    for each_search_data, result in zip(search_data, results):
        time.sleep(1)
        each_search_data['content'] = result.get()
        each_search_data['doc_tokens'] = list(jieba.cut(each_search_data['content']))
    return search_data


# if __name__ == '__main__':
#     start_time = time.time()
#     data = crawl("我和我的祖国七位导演都是谁？")
#     with open('spider_example.json', 'w') as wtf:
#         for var in data:
#             wtf.write(json.dumps(var, ensure_ascii=False)+'\n')
#     print(f'耗时: {time.time() - start_time}')