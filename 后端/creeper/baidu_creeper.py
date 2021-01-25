# encoding=utf-8

import json
import re
import time
import urllib
from functools import reduce

import bs4
import jieba
import lxml
import requests
from bs4 import BeautifulSoup
 
from creeper import url2io

tpl_list = [
    'se_com_default',  # 默认其他网站
    'exactqa',  # 精准回答
    'bk_polysemy',  # 百度百科
    'url',
    'jingyan_summary'  # 百度经验
]

api1 = url2io.API('HMTEF2G9SzySmZ7DAWN0Rw')
api2 = url2io.API('yCnOWq_vTfSd7svSDH5f9Q')


def creeper(word, num=5):
    '''

    :param word: 爬取关键字
    :param num: 要爬取的网页数量
    :return:
        titles: 文章标题
        abstracts:  摘要
        links:  链接
        contents:  主要内容
    '''
    st = time.time()

    titles = []  # 文章标题
    abstracts = []  # 摘要
    links = []  # 链接
    contents = []  # 主要内容

    for pn in range(0, 10):
        if len(contents) >= num:
            break

        url = 'http://www.baidu.com.cn/s?wd=' + urllib.parse.quote(word) + '&pn={:d}'.format(
            pn * 10)  # word为关键词，pn是百度用来分页的..
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, compress',
            'Accept-Language': 'en-us;q=0.5,en;q=0.3',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
        }  # 定义头文件，伪装成浏览器

        while True:
            print('Some error, try again...')
            req = urllib.request.Request(url, headers=headers)
            page = urllib.request.urlopen(req)
            soup = BeautifulSoup(page.read().decode('utf8', 'ignore'), 'lxml')
            content = soup.find('div', {'id': 'content_left'})
            if content is not None:
                break

        divs = content.find_all('div', {'class': re.compile("result*")})
        for div in divs:
            # print(div.get('tpl'))
            if div.get('tpl') in tpl_list:
                # 属于可以提取的网页
                tag = div.find('a')
                link = tag.get('href')

                abstract = None
                try:
                    #  一般的摘要位置
                    abstract = div.find(
                        name="div",
                        attrs={"class": re.compile("c-abstract")}
                    ).text.replace("\"", "")
                except:
                    #  exactqa的摘要位置
                    try:
                        abstract = div.find(
                            name="span",
                            attrs={"class": re.compile("c-gap-right-small")}
                        ).text.replace("\"", "")
                    except:
                        pass

                if link.startswith('http') == False:
                    continue
                content = None
                try:
                    t1 = time.time()
                    content = api1.article(url=link,
                                           fields=['text'])
                    t2 = time.time()
                    print("Time cost: {:f}".format(t2 - t1))
                except Exception as e:
                    print('error')
                    print(e)

                if content is None:
                    print(link)
                    continue
                else:
                    content = content['text'].replace(
                        '\r', '').replace('\n', '')
                    links.append(link)
                    titles.append(tag.text.replace("\"", ""))
                    if abstract is None:
                        abstract = content[:100]
                    abstracts.append(abstract)
                    contents.append(content)

            if len(contents) >= num:
                break

    ed = time.time()
    print("Total time cost: {:f}".format(ed - st))
    examples = []
    question_id = 1
    for content in contents:
        python2json = {}
        python2json['question_id'] = question_id
        question_id += 1
        python2json['question'] = word
        seg_list = jieba.cut(content)
        doc_tokens = list(seg_list)
        python2json['doc_tokens'] = doc_tokens
        examples.append((python2json))

    return links, titles, abstracts, examples, contents


def creeper_v1(word, num=5):
    '''

    :param word: 爬取关键字
    :param num: 要爬取的网页数量
    :return:
        titles: 文章标题
        abstracts:  摘要
        links:  链接
        contents:  主要内容
    '''
    st = time.time()

    titles = []  # 文章标题
    abstracts = []  # 摘要
    links = []  # 链接
    contents = []  # 主要内容

    for pn in range(0, 10):
        if len(contents) >= num:
            break

        url = 'http://www.baidu.com.cn/s?wd=' + urllib.parse.quote(word) + '&pn={:d}'.format(
            pn * 10)  # word为关键词，pn是百度用来分页的..
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate, compress',
            'Accept-Language': 'en-us;q=0.5,en;q=0.3',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'
        }  # 定义头文件，伪装成浏览器

        while True:
            print('Some error, try again...')
            req = urllib.request.Request(url, headers=headers)
            page = urllib.request.urlopen(req)
            soup = BeautifulSoup(page.read().decode('utf8', 'ignore'), 'lxml')
            content = soup.find('div', {'id': 'content_left'})
            if content is not None:
                break

        divs = content.find_all('div', {'class': re.compile("result*")})
        for div in divs:
            # print(div.get('tpl'))
            if div.get('tpl') in tpl_list:
                # 属于可以提取的网页
                tag = div.find('a')
                link = tag.get('href')

                abstract = None
                try:
                    #  一般的摘要位置
                    abstract = div.find(
                        name="div",
                        attrs={"class": re.compile("c-abstract")}
                    ).text.replace("\"", "")
                except:
                    #  exactqa的摘要位置
                    try:
                        abstract = div.find(
                            name="span",
                            attrs={"class": re.compile("c-gap-right-small")}
                        ).text.replace("\"", "")
                    except:
                        pass

                if link.startswith('http') == False:
                    continue
                content = None
                try:
                    t1 = time.time()
                    content = api1.article(url=link,
                                           fields=['text'])
                    t2 = time.time()
                    print("Time cost: {:f}".format(t2 - t1))
                except Exception as e:
                    print('error')
                    print(e)

                if content is None:
                    print(link)
                    continue
                else:
                    content = content['text'].replace(
                        '\r', '').replace('\n', '')
                    links.append(link)
                    titles.append(tag.text.replace("\"", ""))
                    if abstract is None:
                        abstract = content[:100]
                    abstracts.append(abstract)
                    contents.append(content)

            if len(contents) >= num:
                break

    ed = time.time()
    print("Total time cost: {:f}".format(ed - st))
    examples = []
    indexs = range(1,len(links)+1)
    for index, link, title, abstract, content in zip(indexs, links, titles, abstracts, contents) :
        example = {
            'question_id': index,
            'question': word,
            'title': title,
            'abstract': abstract,
            'source_link': link,
            'content': content,
            'doc_tokens': list(jieba.cut(content))
        }
        examples.append(example)


    return examples


# if __name__ == '__main__':
#     question = "我和我的祖国七位导演都是谁？"
#     examples = creeper_v1(question, 3)
#     with open('url2io_example.json', 'w') as wtf:
#         for example in examples:
#             wtf.write(json.dumps(example, ensure_ascii=False) + '\n')
