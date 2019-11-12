import math

import json
import logging
import os
import sys
import numpy as np
from gensim.models import KeyedVectors

sys.path.insert(0, os.getcwd())
from Model import PeopleDaily, db, sql_execute

logger = logging.getLogger('assign_sense')
handler = logging.FileHandler('assign_sense.log')
fmt = '%(asctime)s %(levelname)-6s: %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def load_vocab(path):
    vocab = {}
    for line in open(path, encoding='utf8'):
        word, sense_count = line.strip().split()
        vocab[word] = int(sense_count)
    return vocab


def get_senses(word, sense_count):
    return map(lambda x: '{}_s{}'.format(word, x), range(sense_count.get(word, 1)))


def sim(vec1, vec2):
    return vec1.dot(vec2) / np.linalg.norm(vec1) / np.linalg.norm(vec2)


with db.cursor() as cursor:
    sql_execute(cursor, 'select count(*) as total from Sentence')
    total = cursor.fetchone()['total']
    sql_execute(cursor, 'select fk_sentence_id from SenseInvertedIndex order by id desc limit 1;')
    now_id = cursor.fetchone()
    now_id = 0 if now_id is None else now_id['fk_sentence_id']

wnd_size = 5
dim = 300
basename = 'DCServer/modelfiles/people-MSSG-v1.3'
sense_kv = KeyedVectors.load(basename + '.kv.sc_5.sense')
context_kv = KeyedVectors.load(basename + '.kv.sc_5.context')
global_kv = KeyedVectors.load(basename + '.kv.sc_5.global')
vocab = load_vocab(basename + '.txt.sc_5.vocab')
sense_count = json.load(open(basename + '.txt.sc_5.sense_count'))

print(now_id)
logger.info('start')


def create_inverted_sense_index(sentence):
    sql = 'INSERT INTO {}(token, start_offset, end_offset, pos, fk_sentence_id) VALUES '
    fk_sent_id = sentence['id']
    part_of_speech = sentence['part_of_speech']
    try:
        words = list(map(lambda x: x.split('/')[0], part_of_speech.split()))
    except Exception as e:
        logger.error(e)
        logger.error(id, part_of_speech)
        return
    v = np.zeros((len(words), dim))
    for i, word in enumerate(words):
        if word in global_kv:
            v[i, ] = global_kv[word]
    start_offset = 0
    bulk = []
    for i, word in enumerate(words):
        end_offset = start_offset + len(word)
        try:
            sense_token = max(get_senses(word, sense_count), key=lambda x: sim(context_kv[x],(np.sum(v[max(0, i-wnd_size):min(len(words), i+wnd_size+1)], axis=0)-v[i, ])/(2*wnd_size)))
        except (KeyError, ValueError):
            sense_token = '{}_s0'.format(word)
        bulk.extend([sense_token, start_offset, end_offset, i, fk_sent_id])
        start_offset = end_offset
    sql += ','.join(['(%s, %s, %s, %s, %s)'] * (len(bulk) // 5))
    try:
        with db.cursor() as cursor:
            sql_execute(cursor, sql.format('SenseInvertedIndex'), bulk)
        db.commit()
    except Exception as e:
        print(e)
        print(sentence)


page_size = 5000
for page_num in range(math.ceil(total / page_size)):
    if page_num % 1 == 0 and page_num > 0:
        logger.info('{} {}'.format(page_num, page_num / math.ceil(total / page_size)))
    sentences = PeopleDaily.where_sentence(fields=['id', 'part_of_speech'], page_num=page_num, page_size=page_size)
    for sentence in sentences:
        create_inverted_sense_index(sentence)
logger.info('finish')
