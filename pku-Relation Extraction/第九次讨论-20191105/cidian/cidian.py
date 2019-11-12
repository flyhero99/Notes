#!/usr/bin/env python
# coding: utf-8
import requests
from bs4 import BeautifulSoup
import json
import string
import datetime
import redis
import multiprocessing
from itertools import repeat


# 传入的两个参数是首字母和页码
def worker(pinyin, page):
    # 用redis来记录当前的参数是否处理过，处理过则跳过
    r = redis.StrictRedis(db=2)
    if r.get('{}_{}'.format(pinyin, page)) is not None:
        print(datetime.datetime.now(), pinyin, page, 'skipped')
        return
    print(datetime.datetime.now(), pinyin, page, 'start')

    # 将爬取的内容逐行写入
    with open('data/{}_{}.lined_json'.format(pinyin, page), 'w', encoding='utf8', buffering=1) as of:
        # 下面的页面是选定首字母和页码后的词语目录
        words_url = 'http://cidian.xpcha.com/pinyin_{}_{}.html'.format(pinyin, page)
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'Host': 'cidian.xpcha.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
            'Referer': words_url
        }
        ret = requests.get(words_url, headers=headers)
        bs = BeautifulSoup(ret.text, 'lxml')

        # select是利用css选择器的语法进行选择
        # 选择所有的词语
        words = bs.select('dl.shaixuan_6 dd a')
        for word in words:
            # 词条的具体页面
            detail_url = 'http://cidian.xpcha.com/{}'.format(word['href'])
            token = word.text.strip()
            ret = requests.get(detail_url, headers)
            bs = BeautifulSoup(ret.text, 'lxml')
            # 把基本解释和详细解释部分的html直接作为string保存起来
            jbjs = bs.select('#jbjs')
            if jbjs:
                jbjs = str(jbjs[0])
            else:
                jbjs = ''
            xxjs = bs.select('#xxjs')
            if xxjs:
                xxjs = str(xxjs[0])
            else:
                xxjs = ''
            print(json.dumps({'word': token, 'jbjs': jbjs, 'xxjs': xxjs}, ensure_ascii=False), file=of)
    print(datetime.datetime.now(), pinyin, page, 'finished', len(words))
    # 标记当前任务已完成
    r.set('{}_{}'.format(pinyin, page), len(words))
    return len(words)


if __name__ == '__main__':
    fin = False
    while not fin:
        try:
            # 使用进程池，提高爬取效率
            pool = multiprocessing.Pool(12)
            for pinyin in string.ascii_uppercase:
                menu_url = 'http://cidian.xpcha.com/pinyin_{}.html'.format(pinyin)
                # 伪造的header，但是其实没必要，对方完全没有反爬措施
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                    'Host': 'cidian.xpcha.com',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
                }
                headers['Referer'] = menu_url

                ret = requests.get(menu_url, headers=headers)
                bs = BeautifulSoup(ret.text, 'lxml')

                # 查看这个拼音首字母一共有多少页
                try:
                    total_count = bs.select('.fenye a')[-2]['href'].split('_')[-1].split('.')[0]
                except Exception:
                    continue
                # 提交所有worker
                pm = pool.starmap(worker, zip(repeat(pinyin), range(1, int(total_count)+1)))
            fin = True
        except Exception as e:
            print(repr(e))
