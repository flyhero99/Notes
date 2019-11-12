import os
import datetime

import requests
import json
from bs4 import BeautifulSoup
import multiprocessing
import redis

# 检查中发现，词典页给出的词语并不全，所以根据我们的语料库，检索得到了更多词语
def worker(index, query):
    # 同样，处理过的词就不再处理了
    r = redis.StrictRedis(db=3)
    if r.get(query) is not None:
        return
    print(datetime.datetime.now(), index, query, end=' ')
    # 这是检索页的URL，禁止重定向，让我们可以知道这次检索是返回了多个结果还是直接跳到了结果页
    query_url = 'http://cidian.xpcha.com/query_{}.html'.format(query)
    ret = requests.get(query_url, allow_redirects=False)
    token = query
    if ret.status_code == 200:
        # 200的话是检索到了多个结果
        bs = BeautifulSoup(ret.text, 'lxml')
        a = bs.select('dl.shaixuan_1 dd a')
        if not a:
            r.set(query, 'None')
            print('no result')
            return None
        # 我们选取检索到的第一个结果，保险起见，不用查询词，而是结果词作为token
        token = a[0].span.text.strip('：')
        print('query:', token)
        # 拼接出结果页，注意，所有的结果页都要采用https协议，因为http协议的URL有时会再次重定向到广告页
        result_url = 'https://cidian.xpcha.com/' + a[0]['href']
        ret = requests.get(result_url)
    else:
        # 发生了重定向，认为是直接跳转到了结果页
        print('redirect')
        try:
            # 直接从header里获取重定向地址
            result_url = 'https://cidian.xpcha.com/' + ret.headers['Location']
        except KeyError:
            return None
        ret = requests.get(result_url)

    # 后面的逻辑就和爬虫中一样了
    bs = BeautifulSoup(ret.text, 'lxml')
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
    of = open('data/append.lined_json', 'a')
    print(json.dumps({'word': token, 'jbjs': jbjs, 'xxjs': xxjs}, ensure_ascii=False), file=of)
    of.close()
    return True


if __name__ == '__main__':
    # 从我们的语料库里读入所有词语
    corpus = {}
    for line in open('count.csv'):
        a, b = line.strip().split('\t')
        corpus[a] = int(b)

    corpus_words = set(corpus.keys())

    # 读入所有爬取到的词语
    data = []
    for a, b, c in os.walk('data'):
        for cc in c:
            data.extend(map(json.loads, open(os.path.join(a, cc))))
    words = {d['word'] for d in data if d['jbjs'] or d['xxjs']}

    # 两个集合做差并根据词频排序，得到我们的待爬列表
    diff = list(filter(lambda x: len(x) > 1, corpus_words.difference(words)))
    diff = sorted(diff, key=lambda x: corpus[x], reverse=True)

    pool = multiprocessing.Pool(12)
    pm = pool.starmap(worker, zip(range(1, len(diff)+1), diff))
