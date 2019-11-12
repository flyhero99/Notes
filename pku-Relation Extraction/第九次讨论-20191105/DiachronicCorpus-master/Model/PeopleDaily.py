import hashlib
import json
import random
from functools import partial

from Model import db, sql_execute
from Model.utils import logger


def create_document(source, date, path):
    sql = 'INSERT INTO Document(date, source, path) VALUES (%s, %s, %s)'
    with db.cursor() as cursor:
        cursor.execute(sql, [date, source, path])
        db.commit()
        return cursor.lastrowid


def create_sentence(content, part_of_speech, pos, fk_doc_id):
    sql = 'INSERT INTO Sentence(content, part_of_speech, pos, fk_document_id) VALUES (%s, %s, %s, %s)'
    with db.cursor() as cursor:
        cursor.execute(sql, [content, part_of_speech, pos, fk_doc_id])
        db.commit()
        return cursor.lastrowid


# 按bulk批量插入句子，在优化了数据库cache pool的大小之后，直接用上一个单条插入就够用了
bulk_create_sentence_in_bulk = []
def create_sentence_in_bulk(content, part_of_speech, pos, fk_doc_id):
    bulk_create_sentence_in_bulk.extend([content, part_of_speech, pos, fk_doc_id])
    if len(bulk_create_sentence_in_bulk) >= 100:
        launch_sentence_bulk()


def launch_sentence_bulk():
    sql = 'INSERT INTO Sentence(content, part_of_speech, pos, fk_document_id) VALUES '
    return launch_bulk(sql, bulk_create_sentence_in_bulk, 4)


def launch_bulk(sql, bulk, n):
    try:
        sql += ','.join(['({})'.format(','.join(['%s'] * n))] * (len(bulk) // n))
        with db.cursor() as cursor:
            cursor.execute(sql, bulk)
            db.commit()
            bulk.clear()
    except Exception as e:
        print(e)


# 创建倒排索引
# 倒排索引的数量比较大，所以采用了bulk插入
def create_inverted_index(sentence):
    sql = 'INSERT INTO {}(token, start_offset, end_offset, pos, fk_sentence_id) VALUES '
    fk_sent_id = sentence['id']
    pos_tag = sentence['part_of_speech'].split()
    start_offset = 0
    w_bulk = []
    p_bulk = []
    for cnt, pt in enumerate(pos_tag):
        v = pt.split('/')
        w_token = '/'.join(v[:-1])
        p_token = v[-1]
        end_offset = start_offset + len(w_token)
        w_bulk.extend([w_token, start_offset, end_offset, cnt, fk_sent_id])
        p_bulk.extend([p_token, start_offset, end_offset, cnt, fk_sent_id])
        start_offset = end_offset
    sql += ','.join(['(%s, %s, %s, %s, %s)'] * (len(w_bulk) // 5))
    try:
        with db.cursor() as cursor:
            sql_execute(cursor, sql.format('WordInvertedIndex'), w_bulk)
            sql_execute(cursor, sql.format('PosInvertedIndex'), p_bulk)
        db.commit()
    except Exception as e:
        print(e)
        print(sentence)


# 通用的where语句
def where(tablename, fields='*', page_num=None, page_size=None, **kwargs):
    sql = 'SELECT {} FROM {}'.format(','.join(fields), tablename)
    if len(kwargs) > 0:
        sql += ' WHERE {}'.format(' and '.join(map(lambda x: x + '=%s', kwargs.keys())))
    args = list(kwargs.values())
    if page_num is not None and page_size is not None:
        sql += ' limit %s, %s'
        args.extend([page_num * page_size, page_size])
    with db.cursor() as cursor:
        sql_execute(cursor, sql, args)
        return cursor.fetchall()


# 针对Sentence和Document表的where的别名
where_sentence = partial(where, 'Sentence')
where_document = partial(where, 'Document')


# 获取词语的pmi
@logger
def get_npmi(token):
    sql = '''select token_and_count.token, token_and_count.date, cnt,
        aux_word_count.count as x_cnt, aux_word_count2.count as y_cnt,
        log(aux_word_count.count*aux_word_count2.count/year_count/year_count)/log(cnt/year_count)-1 as npmi from
        (select token, date, count(*) as cnt, (select sum(count) from aux_word_count where date=date) as year_count from
        (select t2.token, rdd_date as date from
        (select token, pos, fk_sentence_id from WordInvertedIndex where token=%s) t1
        left join
        (select token, pos, fk_sentence_id, rdd_date from WordInvertedIndex) t2
        on t1.fk_sentence_id=t2.fk_sentence_id
        where abs(t1.pos-t2.pos)<5 and t1.pos!=t2.pos) cooccur
        group by token, date) as token_and_count
        left join aux_word_count
        on token_and_count.token=aux_word_count.token and token_and_count.date=aux_word_count.date
        left join aux_word_count as aux_word_count2
        on aux_word_count2.token=%s and token_and_count.date=aux_word_count2.date'''
    with db.cursor() as cursor:
        sql_execute(cursor, sql, [token, token])
        results = cursor.fetchall()
    return results


@logger
def get_tmp_phrase_table(tokens):
    myMd5 = hashlib.md5()
    myMd5.update('|'.join(tokens).encode())
    table_id = 'tmp_table_{}'.format(myMd5.hexdigest())
    sql = '''create temporary table if not exists {}
            select t0.pos as spos, t{}.pos as epos, t0.start_offset, t{}.end_offset, 
            t0.fk_sentence_id, t0.rdd_date as date from 
            WordInvertedIndex as t0'''.format(table_id, len(tokens) - 1, len(tokens) - 1)
    sql1 = '''left join
            WordInvertedIndex as t{}
            on t0.fk_sentence_id=t{}.fk_sentence_id and t{}.pos=t{}.pos-1'''
    for i in range(1, len(tokens)):
        sql = sql + '\n' + sql1.format(i, i, i - 1, i)
    sql = sql + '\nwhere'
    sql = sql + '\n' + ' and '.join(['t{}.token=%s'.format(x) for x in range(len(tokens))])
    with db.cursor() as cursor:
        sql_execute(cursor, sql, tokens)
    return table_id


# 获取短语的pmi
@logger
def get_phrase_npmi(tokens):
    tmp_table = get_tmp_phrase_table(tokens)
    count_table = tmp_table+'_count'
    sql0 = '''create temporary table if not exists {}
        select date, count(*) as count
        from {}
        group by date'''.format(count_table, tmp_table)
    sql = '''select token_and_count.token, token_and_count.date, cnt,
        aux_word_count.count as x_cnt, phrase_count.count as y_cnt,
        log(aux_word_count.count*phrase_count.count/year_count/year_count)/log(cnt/year_count)-1 as npmi from
        (select token, date, count(*) as cnt, (select sum(count) from aux_word_count where date=date) as year_count from
        (select t2.token, rdd_date as date from
        {} as t1
        left join
        (select token, pos, fk_sentence_id, rdd_date from WordInvertedIndex) t2
        on t1.fk_sentence_id=t2.fk_sentence_id
        where t1.spos-5<t2.pos and t1.epos+5>t2.pos and t1.spos!=t2.pos and t1.epos!=t2.pos) cooccur
        group by token, date) as token_and_count
        left join aux_word_count
        on token_and_count.token=aux_word_count.token and token_and_count.date=aux_word_count.date
        left join 
        {} as phrase_count
        on token_and_count.date=phrase_count.date'''.format(tmp_table, count_table)
    with db.cursor() as cursor:
        sql_execute(cursor, sql0)
        sql_execute(cursor, sql)
        results = cursor.fetchall()
    return results


# 获取词性的pmi
@logger
def get_tag_npmi(token, pos):
    sql = '''select src_tag, token_and_count.date, co_tag, cnt, word_cnt.count as x_cnt, aux_pos_count.count as y_cnt,
        log(word_cnt.count*aux_pos_count.count/year_count/year_count)/log(cnt/year_count)-1 as npmi,
         log(cnt*year_count/word_cnt.count/aux_pos_count.count) as pmi from
        (select *, count(*) as cnt, (select sum(count) from aux_word_count where date=date) as year_count from
        (select t1.token as src_word, t2.token as src_tag, date, t3.token as co_tag from
        (select token, pos, fk_sentence_id, rdd_date as date from WordInvertedIndex where token=%s) t1
        left join
        (select token, pos, fk_sentence_id from PosInvertedIndex) t2
        on
        t1.fk_sentence_id=t2.fk_sentence_id and t1.pos=t2.pos
        left join
        (select token, pos, fk_sentence_id from PosInvertedIndex) t3
        on
        t1.fk_sentence_id=t3.fk_sentence_id and t1.pos=t3.pos{}) cooccur
        group by src_tag, date, co_tag) token_and_count
        left join
        aux_word_pos_count as word_cnt
        on token_and_count.src_word=word_cnt.word and token_and_count.src_tag=word_cnt.tag and token_and_count.date=word_cnt.date
        left join
        aux_pos_count
        on token_and_count.co_tag=aux_pos_count.token and token_and_count.date=aux_pos_count.date'''
    sql = sql.format('+1') if pos == 'left' else sql.format('-1')
    with db.cursor() as cursor:
        sql_execute(cursor, sql, [token])
        results = cursor.fetchall()
    return results


# 获取共现次数
@logger
def get_cooccur_count(src_word, src_tag, co_table, co_tag, date, pos_range):
    sql = '''select co_word, count(*) as cnt from
(select t1.token as src_word, t2.token as src_tag, date, t3.token as co_tag, t4.token as co_word from
(select token, pos, fk_sentence_id, rdd_date as date from WordInvertedIndex) t1
left join
(select token, pos, fk_sentence_id from PosInvertedIndex) t2
on
t1.fk_sentence_id=t2.fk_sentence_id and t1.pos=t2.pos
left join
(select token, pos, fk_sentence_id from {}) t3
on
t1.fk_sentence_id=t3.fk_sentence_id and t1.pos+{}<=t3.pos and t1.pos+{}>t3.pos and t1.pos != t3.pos
left join
(select token, pos, fk_sentence_id from WordInvertedIndex) t4
on
t3.fk_sentence_id=t4.fk_sentence_id and t3.pos=t4.pos) cooccur
where {}
group by co_word
order by cnt desc'''
    # 如果传入的参数是星号，则不添加这个列的限制
    criterias = []
    for cr in ['src_word', 'src_tag', 'co_tag', 'date']:
        if locals()[cr] != '*':
            criterias.append(cr)
    # 根据限制的数量，动态生成查询语句
    sql = sql.format(co_table, pos_range[0], pos_range[1], ' and '.join(map(lambda x: x+'=%s', criterias)))
    with db.cursor() as cursor:
        args = []
        for cr in criterias:
            args.append(locals()[cr])
        sql_execute(cursor, sql, args)
        results = cursor.fetchall()
    return results


# 获取共现实例
@logger
def get_cooccur(table1, table2, token1, token2, pos_range, date):
    sql = '''select t1.start_offset as so1, t1.end_offset as eo1, t2.start_offset as so2, t2.end_offset as eo2, 
Sentence.content, Sentence.id as sentence_id
from {} as t1
left join
{} as t2
on t1.fk_sentence_id=t2.fk_sentence_id
left join
Sentence
on t1.fk_sentence_id=Sentence.id
left join
Document
on Sentence.fk_document_id=Document.id
where t1.token=%s and t2.token=%s and t1.pos+{}<=t2.pos and t1.pos+{}>t2.pos and t1.pos != t2.pos
'''
    sql = sql.format(table1, table2, pos_range[0], pos_range[1])
    args = [token1, token2]
    # 同上，判断是否添加对日期的限制
    if date != '*':
        sql += ' and Document.date=%s'
        args.append(date)
    with db.cursor() as cursor:
        sql_execute(cursor, sql, args)
        results = cursor.fetchall()
    return results


# 按年份获取频率
@logger
def get_count(token):
    sql ='''select rdd_date as date, count(*) as cnt
from
WordInvertedIndex
where token=%s
group by rdd_date'''
    with db.cursor() as cursor:
        sql_execute(cursor, sql, [token])
        results = cursor.fetchall()
    return results


# 分页获取实例
def get_instance(token, date, page_num, page_size):
    sql = '''select t1.start_offset as so, t1.end_offset as eo, Sentence.content, Sentence.id as sentence_id,
    fk_document_id, Sentence.pos as sentence_pos
    from WordInvertedIndex as t1
    left join
    Sentence
    on t1.fk_sentence_id=Sentence.id
    left join
    Document
    on Sentence.fk_document_id=Document.id
    where t1.token=%s
    '''
    args = [token]
    if date != '*':
        sql += ' and Document.date=%s'
        args.append(date)
    sql += ' limit %s, %s'
    args.extend([page_num * page_size, page_size])
    with db.cursor() as cursor:
        sql_execute(cursor, sql, args)
        results = cursor.fetchall()
    return results


# 这是按标签频率排序后的词性list
def get_tags():
    return ['n', 'v', 'u', 'd', 'm', 'p', 'a', 'r', 'q', 'c', 't', 'g', 'f', 'b', 'l', 's', 'x', 'y', 'k', 'z',
            'o', 'e', 'h', '一', 'n_newword', 'url', 'w']
    # sql = 'select distinct token from PosInvertedIndex'
    # with db.cursor() as cursor:
    #     sql_execute(cursor, sql)
    #     results = cursor.fetchall()
    # return list(map(lambda x: x['token'], results))


def get_years():
    sql = 'select distinct date from Document'
    with db.cursor() as cursor:
        sql_execute(cursor, sql)
        results = cursor.fetchall()
    return list(map(lambda x: x['date'].strftime('%Y'), results))


# 下面是几个辅助表的构造语句
def create_aux_word_count():
    sql = '''
    create table aux_word_count
    (primary key (token, date))
    engine=MyISAM
    select token, date, count(*) as count
    from (select token, fk_sentence_id from WordInvertedIndex) t1 
    left join
    (select id, fk_document_id from Sentence) t2
    on t1.fk_sentence_id=t2.id
    left join
    (select id, date from Document) t3
    on t2.fk_document_id=t3.id
    group by token, date;'''
    with db.cursor() as cursor:
        sql_execute(cursor, sql)
        db.commit()


def create_aux_word_pos_count():
    sql = '''
    create table aux_word_pos_count
    (primary key (word, tag, date), 
    key (word),
    key (tag),
    key (date),
    key (word, tag),
    key (word, date),
    key (tag, date))
    engine=MyISAM
    select word, tag, date, count(*) as count
    from (select token as word, pos, fk_sentence_id from WordInvertedIndex) t1 
    left join
    (select token as tag, pos, fk_sentence_id from PosInvertedIndex) t2
    on
    t1.fk_sentence_id=t2.fk_sentence_id and t1.pos=t2.pos
    left join
    (select id, fk_document_id from Sentence) t3
    on t1.fk_sentence_id=t3.id
    left join
    (select id, date from Document) t4
    on t3.fk_document_id=t4.id
    group by word, tag, date;'''
    with db.cursor() as cursor:
        sql_execute(cursor, sql)
        db.commit()


def create_rdd_date():
    sql = '''
    update WordInvertedIndex
    left join
    Sentence
    on WordInvertedIndex.fk_sentence_id=Sentence.id
    left join
    Document
    on Sentence.fk_document_id=Document.id
    set
    WordInvertedIndex.rdd_date=Document.date'''
    with db.cursor() as cursor:
        sql_execute(cursor, sql)
        db.commit()


if __name__ == '__main__':
    get_npmi('快速')

