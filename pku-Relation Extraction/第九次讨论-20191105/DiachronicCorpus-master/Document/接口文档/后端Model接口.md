# 后端Model接口

本文档将提供后端Model层，即数据库查询级别接口的文档。

有些接口为了通用型，会动态产生查询语句，在本文档中会以最复杂的情况给出代码。

代码中的`%s`为占位符，运行时会被替换成合适的变量值。

TODO: 还有一些建表、建索引等不涉及业务的函数没有放在文档里，后续有时间补上。

TODO: 数据库语句的注释待后续加上。

## 获取共现词pmi分布

* function: get_npmi()
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| token  | true  | string | 中心词         |

* 数据库语句:
```SQL
select token_and_count.token, token_and_count.date, cnt,
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
on aux_word_count2.token=%s and token_and_count.date=aux_word_count2.date
```

## 获取共现词性pmi分布

* function: get_npmi()
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| token  | true  | string | 中心词         |
| pos  | true  | 'left' or 'right' | 邻接方向         |

* 数据库语句:
```SQL
select src_tag, token_and_count.date, co_tag, cnt, word_cnt.count as x_cnt, aux_pos_count.count as y_cnt,
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
t1.fk_sentence_id=t3.fk_sentence_id and t1.pos=t3.pos+1) cooccur
group by src_tag, date, co_tag) token_and_count
left join
aux_word_pos_count as word_cnt
on token_and_count.src_word=word_cnt.word and token_and_count.src_tag=word_cnt.tag and token_and_count.date=word_cnt.date
left join
aux_pos_count
on token_and_count.co_tag=aux_pos_count.token and token_and_count.date=aux_pos_count.date
```

## 获取词语的某词性共现词频率

* function: get_cooccur_count()
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| src_word  | true  | string | 中心词         |
| src_tag  | true  | string | 中心词性         |
| co_tag  | true  | string | 共现词性         |
| date  | true  | string | 年份         |
| pos_range  | true  | array | token2相对于token1的合法位置         |

* 数据库语句
```SQL
select co_word, count(*) as cnt from
(select t1.token as src_word, t2.token as src_tag, date, t3.token as co_tag, t4.token as co_word from
(select token, pos, fk_sentence_id, rdd_date as date from WordInvertedIndex) t1
left join
(select token, pos, fk_sentence_id from PosInvertedIndex) t2
on
t1.fk_sentence_id=t2.fk_sentence_id and t1.pos=t2.pos
left join
(select token, pos, fk_sentence_id from PosInvertedIndex) t3
on
t1.fk_sentence_id=t3.fk_sentence_id and t1.pos+{}<=t3.pos and t1.pos+{}>t3.pos and t1.pos != t3.pos
left join
(select token, pos, fk_sentence_id from WordInvertedIndex) t4
on
t3.fk_sentence_id=t4.fk_sentence_id and t3.pos=t4.pos) cooccur
where src_word=%s and src_tag=%s and co_tag=%s and date=%s
group by co_word
order by cnt desc
```

## 获取两个token共现的实例

* function: get_cooccur()
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| table1  | true  | 'word' or 'tag' | token1的类型         |
| table2  | true  | 'word' or 'tag' | token2的类型         |
| token1  | true  | string | token1         |
| token2  | true  | string | token2         |
| pos_range  | true  | array | token2相对于token1的合法位置         |
| date  | true  | string | 年份         |

* 数据库语句
```SQL
select t1.start_offset as so1, t1.end_offset as eo1, t2.start_offset as so2, t2.end_offset as eo2,
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
where t1.token=%s and t2.token=%s and t1.pos+{}<=t2.pos and t1.pos+{}>t2.pos and t1.pos != t2.pos and Document.date=%s
```

## 获取词语每个年份的频率

* function: get_count()
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| token  | true  | string | token         |

* 数据库语句
```SQL
select rdd_date as date, count(*) as cnt
from
WordInvertedIndex
where token=%s
group by rdd_date
```

## 分页获取实例

* get_instance()
* 参数

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| token  | true  | string | token         |
| date  | true  | string | date         |
| page_num  | true  | int | 分页页码（从0开始）         |
| page_size  | true  | int | 分页大小         |

* 数据库语句
```SQL
select t1.start_offset as so, t1.end_offset as eo, Sentence.content, Sentence.id as sentence_id
from WordInvertedIndex as t1
left join
Sentence
on t1.fk_sentence_id=Sentence.id
left join
Document
on Sentence.fk_document_id=Document.id
where t1.token=%s and Document.date=%s
limit %s, %s
```
