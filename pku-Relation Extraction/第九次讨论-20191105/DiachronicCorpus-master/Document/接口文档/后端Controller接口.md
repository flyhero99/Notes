# 后端Controller接口

**WARNING: DEPRECATED**

本文档将提供后端Controller层，也就是URL级别接口的文档。

注意这里的URL与前端的URL应该是由不同的服务器提供的，在单机上，通过端口号区分。

所有后端接口的统一返回值的格式为：

success:

```
{
    "code": 200,
    "msg": "msg",
    "data": {}
}
```

fail:

```
{
    "code": 300,
    "msg": "msg",//失败返回各种错误信息，如curl，validator等
    "data": {}
}
```

因此后续文档将省略code和msg段，只描述data段的结构。

后端接口的data段格式不太统一，主要是受到前端模块的影响，使用起来更方便一些。

## 获取词语的共现词的PMI分布

* 方法: POST
* URL: /get_pmi
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| token  | true  | string | 中心词         |
| pos  | true  | 'left' or 'right' | 方向         |

* 调用的service层方法: [get_npmi()](后端Service接口.md#获取共现词pmi分布)
* 调用的model层方法: 无
* 返回值:

```
{
    bar: {
        1998: {
            npmi: [],
            token: [],
        },
        ...
    },
    scatter: {
        data: [
            [x_index, y_index, value],
            ...
        ],
        dates: [],
        tokens: [],
    }
}
```

## 获取词语的共现词性的PMI分布

* 方法: POST
* URL: /get_tag_pmi
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| token  | true  | string | 中心词         |
| pos  | true  | string | 中心词         |

* 调用的service层方法: [get_tag_npmi()](后端Service接口.md#获取共现词性pmi分布)
* 调用的model层方法: 无
* 返回值:

```
{
    bar_data: {
        data: {
            b: [],
            ...
        },
        tags: [],
        years: []
    },
    river_data: {   // 已弃用
        b: {
            co_tags: [],
            columns: [],
            data: [
                [year, value, co_tag],
                ...
            ],
            index: []
        }
    }
}
```

## 获取词语的某词性共现词频率

* 方法: POST
* URL: /get_cooccur_count
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| src_word  | true  | string | 中心词         |
| src_tag  | true  | string | 中心词性         |
| co_table  | true  | 'word' or 'tag' | co_tag的类型         |
| co_tag  | true  | string | 共现词性         |
| date  | true  | string | 年份         |
| pos_range  | true  | array | token2相对于token1的合法位置         |

* 调用的service层方法: 无
* 调用的model层方法: [get_tag_cooccur_count()](后端Model接口.md#获取词语的某词性共现词频率)
* 返回值:

```
[{
    co_word: 共现词,
    cnt: 词频
},
...
]
```

## 获取两个token共现的实例

* 方法: POST
* URL: /get_cooccur
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| table1  | true  | 'word' or 'tag' | token1的类型         |
| table2  | true  | 'word' or 'tag' | token2的类型         |
| token1  | true  | string | token1         |
| token2  | true  | string | token2         |
| pos_range  | true  | array | token2相对于token1的合法位置         |
| date  | true  | string | 年份         |

* 调用的service层方法: 无
* 调用的model层方法: [get_cooccur()](后端Model接口.md#获取两个token共现的实例)
* 返回值:

```
[{
    so1: token1的start_offset,
    so2: token2的start_offset,
    eo1: token1的end_offset,
    eo2: token2的end_offset,
    content: 句子内容,
    sentence_id: 句子id
},
...
]
```

## 获取词语每个年份的频率

* 方法: POST
* URL: /get_count
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| token  | true  | string | 中心词         |

* 调用的service层方法: 无
* 调用的model层方法: [get_count()](后端Model接口.md#获取词语每个年份的频率)
* 返回值:

```
{
    count: [],
    date: []
}
```

## 分页获取实例

* 方法: POST
* URL: /get_instance
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| token  | true  | string | token         |
| date  | true  | string | date         |
| page_num  | true  | int | 分页页码（从0开始）         |
| page_size  | true  | int | 分页大小         |

* 调用的service层方法: 无
* 调用的model层方法: [get_count()](后端Model接口.md#分页获取实例)
* 返回值:

```
{
    "content": content,
    "eo": token的end_offset,
    "sentence_id": id,
    "so": token的start_offset
},
```

## 获取句子详情

* 方法: POST
* URL: /get_instance_detail
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| id  | true  | string | sentence_id         |

* 调用的service层方法: 无
* 调用的model层方法: where_sentence()
* 返回值:

```
{
    "content": content,
    "part_of_speech": 分词结果,
    "id": id,
    "fk_document_id": document_id,
    "pos": document中的位置
},
```
