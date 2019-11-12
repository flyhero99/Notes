import json
import os
import sys

import math
import logging
import IPython
from annoy import AnnoyIndex

sys.path.insert(0, os.getcwd())
from Model import PeopleDaily, db, sql_execute
import numpy as np

logger = logging.getLogger('sentence_vector')
handler = logging.FileHandler('sentence_vector.log')
fmt = '%(asctime)s %(levelname)-6s: %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# 读入最近公布的一份巨大的预训练词向量
# 读入后拼成一个字典
word2vec = {}
logger.info('loading word vectors...')
f = open('DataProcess/sgns.renmin.char')
line = next(f)
# 总词数
total_word = int(line.split()[0])
# 词响亮维度
dim = int(line.split()[1])
logger.info('{}, {}'.format(total_word, dim))
for i, line in enumerate(f):
    if i % 10000 == 0:
        logger.debug('{} {} {}'.format(i, total_word, i/total_word))
    v = line.split()
    word2vec[v[0]] = np.array([float(x) for x in v[1:]])
logger.info('loaded')

# 获取数据库中的句子总数
with db.cursor() as cursor:
    sql_execute(cursor, 'select count(*) as total from Sentence')
    total = cursor.fetchone()['total']

# 句子id和矩阵行数的映射
id2index = {}
index = 0
# 句子向量的矩阵
vectors = np.zeros([total, dim])

# 分页从数据库读入
page_size = 5000
for page_num in range(math.ceil(total/page_size)):
    if page_num % 100 == 0 and page_num > 0:
        logger.info('{} {}'.format(page_num, page_num/math.ceil(total/page_size)))
        logger.info('saving...')
        np.save('DataProcess/vectors.txt', vectors)
        json.dump(id2index, open('DataProcess/id2index.txt', 'w'))
        logger.info('saved')
    sentences = PeopleDaily.where_sentence(fields=['id', 'part_of_speech'], page_num=page_num, page_size=page_size)
    for sentence in sentences:
        id = sentence['id']
        part_of_speech = sentence['part_of_speech']
        try:
            words = list(map(lambda x: x.split('/')[0], part_of_speech.split()))
        except Exception as e:
            logger.error(e)
            logger.error(id, part_of_speech)
            continue
        tmp = np.zeros([1, dim])
        cnt = 0
        for word in words:
            if word in word2vec:
                tmp += word2vec[word]
                cnt += 1
        # 如果整个句子的词都不在字典中，跳过
        if cnt == 0:
            if len(part_of_speech.split()) > 5:
                logger.warning('No word in dict: {}'.format(sentence))
            continue
        # average pooling
        tmp /= cnt
        id2index[id] = index
        vectors[index] = tmp
        index += 1
logger.info('finish, {} sentences'.format(index))
logger.info('saving...')
np.save('DataProcess/vectors.txt', vectors)
json.dump(id2index, open('DataProcess/id2index.txt', 'w'))
logger.info('saved')

# f是特征向量的维数
f = 300
t = AnnoyIndex(f)
id2index = json.load(open('DataProcess/id2index.txt'))
vectors = np.load('DataProcess/vectors.txt.npy')

for id in id2index:
    t.add_item(int(id), vectors[id2index[id]])

# 构建10棵树，数量越多越精准，占用内存越多
t.build(10)
t.save('DCServer/10years.ann')