import argparse
import json
import logging
import sys
import os
from collections import OrderedDict

import numpy as np
import IPython
from bs4 import BeautifulSoup
from gensim.models import KeyedVectors
from annoy import AnnoyIndex

sys.path.insert(0, os.getcwd())
from DCServer.CalcServer import *
from DCServer.CalcServer.ttypes import *
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol, TProtocol
from thrift.server import TServer
from DCServer.CalcServer.constants import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)


class CalcServerHandler:
    def __init__(self, word_vec_path, annoy_path, mssg_basename, ontology_path):
        self.wv_from_text = KeyedVectors.load(word_vec_path)
        self.annoy = AnnoyIndex(300)
        self.annoy.load(annoy_path)
        self.sense_vec = KeyedVectors.load(mssg_basename+'.sense')
        logger.info('loading ontology from ' + ontology_path)
        self.ontology = BeautifulSoup(open(ontology_path), 'xml')
        logger.info('loaded ' + ontology_path)
        # self.wv_from_text = KeyedVectors()
        # self.annoy = AnnoyIndex(300)

    def word_distance(self, word_pairs):
        ret = []
        for w1, w2 in word_pairs:
            try:
                ret.append(self.wv_from_text.distance(w1, w2))
            except KeyError:
                ret.append(-1)
        return ret

    def get_sentence_neighbors(self, sentence_id, n):
        return self.annoy.get_nns_by_item(sentence_id, n)

    def get_synonyms(self, word):
        try:
            ret = self.wv_from_text.most_similar(positive=[word])
        except KeyError:
            ret = []
        return [string_double_pair(x[0], x[1]) for x in ret]

    # def get_multi_synonyms(self, word, n):
    #     ret = []
    #     try:
    #         for i in range(0, 10):
    #             ret.append([string_double_pair(key=k.rsplit('_', 1)[0], value=v)
    #                         for k, v in self.sense_vec.most_similar_cosmul('{}_s{}'.format(word, i), topn=n)])
    #     except KeyError:
    #         pass
    #     return ret

    # 这里用similarity域来记录sense_id
    def get_multi_synonyms(self, word, n):
        ret = []
        for sense_id in range(10):
            try:
                synonyms = self._get_synonyms___ontology(word, sense_id, num=n)
                if word in synonyms:
                    continue
                ret.append([string_double_pair(key=k, value=sense_id) for k in synonyms])
            except KeyError:
                break
        return ret

    def _get_synonyms___ontology(self, word, sense_id, num=10):
        node = self.ontology.ontology.find('word', text='{}_s{}'.format(word, sense_id))
        if node is None:
            raise KeyError
        ret = OrderedDict()
        while len(ret) < num and node is not None:
            for ws in node.text.split():
                w, s = ws.split('_s')
                if w != word or int(s) < sense_id:
                    ret[w] = None
            node = node.parent
        return list(ret.keys())[:num]


def run(host, port):
    # 创建服务端
    handler = CalcServerHandler('DCServer/modelfiles/sgns.renmin.char.kv', 'DCServer/10years.ann',
                                'DCServer/modelfiles/people-MSSG-v1.3.kv.sc_5', 'DCServer/ontology.xml')
    processor = CalcServer.Processor(handler)

    # 监听端口
    transport = TSocket.TServerSocket(host, port)

    # 选择传输层
    tfactory = TTransport.TBufferedTransportFactory()

    # 选择传输协议
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    # 创建服务端
    server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)

    logger.info('CalcServer listening %s:%s', host, port)
    server.serve()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Diachronic Corpus Backend Server')
    parser.add_argument('-p', '--port', help='port number', type=int, default=6367)

    args = parser.parse_args()
    run(host='0.0.0.0', port=args.port)
