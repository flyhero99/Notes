import os
import sys

import datetime

sys.path.insert(0, os.getcwd())
from DataProcess.CutSent import CutSent
from Model import PeopleDaily


DATA_PATH = '/home/wuxian/people-daily'


# 弃用
def insert_to_mongodb():
    for a, b, c in os.walk(DATA_PATH):
        for cc in sorted(c):
            with open(os.path.join(a, cc), 'r', encoding='gb18030', errors='ignore') as f:
                cnt = 0
                for lineno, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    lines = line.split('   ')
                    for l in lines:
                        ll = ''.join([x.split('/')[0] for x in l.split()])
                        if not ll:
                            continue
                        sents = CutSent.cut_pos(l)
                        for sent in sents:
                            d = PeopleDaily.MongoDocument()
                            d.doc_id = cc
                            d.sentence_no = cnt
                            d.line_no = lineno + 1
                            d.pos_tag = ' '.join(sent)
                            d.content = ''.join([x.split('/')[0] for x in sent])
                            d.content_length = len(d.content)
                            cnt += 1
                            if not PeopleDaily.MongoDocument.objects(doc_id=d.doc_id, sentence_no=d.sentence_no):
                                d.save()
                    if lineno % 10000 == 0:
                        print(cc, lineno)


# 向mysql插入句子和倒排索引
def insert_to_mysql():
    for a, b, c in os.walk(DATA_PATH):
        for cc in sorted(c):
            if 86 <= int(cc[0:2]) <= 95:
                continue
            results = PeopleDaily.where_document(path=cc)
            if len(results) == 0:
                id = PeopleDaily.create_document('PeopleDaily', '19{}-1-1'.format(cc[:2]), cc)
                results = PeopleDaily.where_document(id=id)
            document = results[0]
            with open(os.path.join(a, cc), 'r', encoding='gb18030', errors='ignore') as f:
                cnt = 0
                for lineno, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    lines = line.split('   ')
                    for l in lines:
                        ll = ''.join([x.split('/')[0] for x in l.split()])
                        if not ll:
                            continue
                        sents = CutSent.cut_pos(l)
                        for sent in sents:
                            content = ''.join([x.split('/')[0] for x in sent])
                            pos_tag = ' '.join(sent)
                            fk_doc_id = document['id']
                            # PeopleDaily.create_sentence_in_bulk(content, pos_tag, cnt, fk_doc_id)
                            id = PeopleDaily.create_sentence(content, pos_tag, cnt, fk_doc_id)
                            sentence = {}
                            sentence['id'] = id
                            sentence['part_of_speech'] = pos_tag
                            PeopleDaily.create_inverted_index(sentence)
                            cnt += 1
                    if lineno % 10000 == 0:
                        print(cc, lineno, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))


if __name__ == '__main__':
    # insert_to_mysql()
    results = PeopleDaily.get_pmi('任务')
