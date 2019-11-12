# 后端Service接口

本文档将提供后端Service层，即函数级别接口的文档。

## 获取共现词pmi分布

* function: get_npmi()
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| token  | true  | string | 中心词         |
| min_count  | false(5)  | int | 最小词频         |
| k  | false(30)  | int | 获取前k个         |

* 调用的model层方法: [get_npmi()](后端Model接口.md#获取共现词pmi分布)
* 行为: 对年份分组，按npmi排序，并取前k个

## 获取共现词性pmi分布

* function: get_tag_npmi()
* 参数:

| 参数名      | 必填   | 类型   | 说明          |
| ---------- | ----- | ------ | ------------ |
| token  | true  | string | 中心词         |
| min_count  | false(5)  | int | 最小词频         |
| k  | false(30)  | int | 获取前k个         |
| pos  | false('left')  | string | 邻接方向         |

* 调用的model层方法: [get_tag_npmi()](后端Model接口.md#获取共现词性pmi分布)
* 行为: 按词性排序，对年份、词性分组，并取前k个
