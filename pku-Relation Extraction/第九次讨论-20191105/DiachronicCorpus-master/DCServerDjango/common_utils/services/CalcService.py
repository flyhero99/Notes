import sys
import os

import IPython
import itertools
import pandas as pd
from thrift.protocol import TBinaryProtocol
from thrift.transport import TSocket, TTransport

sys.path.insert(0, os.getcwd())
from CachedFunction.CacheManager import CacheManager
from CachedFunction.MemRepo import MemRepo
from CachedFunction.RedisRepo import RedisRepo
from DCServer.CalcServer import CalcServer
from Model import PeopleDaily

cm = CacheManager()
rr = RedisRepo()
cm.add_repo(rr, 'redis')


class CalcClient:
    default_host = 'localhost'
    default_port = 6367

    def __init__(self, host=default_host, port=default_port):
        self._transport = TSocket.TSocket(host, port)
        self._transport = TTransport.TBufferedTransport(self._transport)
        protocol = TBinaryProtocol.TBinaryProtocol(self._transport)
        self.client = CalcServer.Client(protocol)

    def open(self):
        self._transport.open()

    def close(self):
        self._transport.close()

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def word_distance(self, word_pairs):
        return self.client.word_distance(word_pairs)

    def get_sentence_neighbors(self, sentence_id, n):
        return self.client.get_sentence_neighbors(sentence_id, n)

    def get_synonyms(self, word):
        ret = self.client.get_synonyms(word)
        return [(r.key, r.value) for r in ret]

    def get_multi_synonyms(self, word, n):
        ret = self.client.get_multi_synonyms(word, n)
        return [[(rr.key, rr.value) for rr in r] for r in ret]


# 获取词语的npmi
@cm.register
def get_npmi(token, min_count=5, k=30, min_y_count=10):
    results = PeopleDaily.get_npmi(token)
    if not results:
        return pd.DataFrame([])
    df = pd.DataFrame(results)
    if df.empty:
        return df
    tmp = df[(df.cnt >= min_count) & (df.y_cnt >= min_y_count)]
    if not tmp.empty and tmp.shape[0] >= k * tmp.drop_duplicates('date').shape[0] * 0.8:
        df = tmp
    # 按年份分组，在组内排序
    df = df.groupby(df.date).apply(pd.DataFrame.sort_values, 'npmi', ascending=False)
    # 按词频过滤，然后按年份分组，取前k个
    df = df.groupby(df.date).head(k)
    return df


# 获取词语的npmi
def get_phrase_npmi(tokens, min_count=2, k=30):
    results = PeopleDaily.get_phrase_npmi(tokens)
    df = pd.DataFrame(results)
    # 按年份分组，在组内排序
    df = df.groupby(df.date).apply(pd.DataFrame.sort_values, 'npmi', ascending=False)
    # 按词频过滤，然后按年份分组，取前k个
    df = df[df.cnt >= min_count].groupby(df.date).head(k)
    return df


# 获取词性的npmi
def get_tag_npmi(token, min_count=5, k=30, pos='left'):
    results = PeopleDaily.get_tag_npmi(token, pos)
    if not results:
        return pd.DataFrame([])
    df = pd.DataFrame(results)
    df = df.sort_values('co_tag')
    # df = df.groupby([df.src_tag, df.date], as_index=False).apply(pd.DataFrame.sort_values, 'npmi', ascending=False)
    # 按词频过滤，按日期和词性分组，取前k个
    df = df[(df.cnt > min_count) & (~df.npmi.isnull())].groupby([df.date, df.src_tag]).head(k)
    return df


# 获取近邻句子
def get_sentence_neighbors(sentence_id, n):
    sentence_id = int(sentence_id)
    with CalcClient() as client:
        return client.get_sentence_neighbors(sentence_id, n)


def calc_links(nodes, thresh=0.5):
    ret = []
    with CalcClient() as client:
        pairs = list(itertools.combinations(nodes, 2))
        dis = client.word_distance(pairs)
        for p, d in zip(pairs, dis):
            if d != -1:
                ret.append({
                    'source': p[0],
                    'target': p[1],
                    'distance': d
                })
    ret = list(filter(lambda x: x['distance'] < thresh, ret))
    return ret


if __name__ == '__main__':
    # df = get_tag_npmi('使用', pos='left')
    # ret = PeopleDaily.get_tag_cooccur_count(src_word='快速', src_tag='b', co_tag='*', date='*', pos='left')
    IPython.embed()
    # print(PeopleDaily.get_phrase_npmi(['上', '下']))
