# top K pmi词集合变迁 计算与展示方案

吴先

wuxian94@pku.edu.cn

[TOC]

## 引言

具体需求为，展示一个词，在各个年份中的PMI前50的词语分布的变迁。本文将介绍运算、通信和展示三个方面的方案，并在末尾给出一个Demo系统。同时，后续功能将会以此为例进行开发。

## 运算方案

本节将介绍在给定一个词语后，如何计算其在不同年份中，与不同词语的PMI值，并会简单介绍性能优化尝试，以及一个更适合展示的从PMI衍生出的指标。

### 总体思路

简单回顾一下存储和索引方案。

对于存储的Sentence，在上面建立两类倒排索引，WordInvertedIndex和PosInvertedIndex。在计算词语PMI的功能中我们只用到WordInvertedIndex。每个条目保存了这个词语出现的句子id和在句子中的位置。

因此，为了计算不同年份、不同词语的PMI，我们将查询分为以下几步。

1. 计算共现关系：将中心词的所有条目与整个倒排索引表根据句子id JOIN在一起，并根据pos差控制窗口大小；
2. 获取年份：根据句子id找到句子，根据句子的文档id找到，根据文档找到年份；
3. 对词语和年份分组：按照共现词和年份进行group by；
4. 获取频率：使用count，分别计算出词对频率、中心词频率和共现词频率；
5. 计算PMI：根据公式计算并返回。

### 优化过程

上述过程非常慢，经过性能分析，得到下图：

![pmi_without_aux_word_count](/Users/wuxian/Documents/计算语言所/DiachronicCorpus/sql_explain/pmi_without_aux_word_count.png)

4.05M行的计算来自于对一年份中词语词频的计算，因此考虑增加一个表，命名为aux_word_count（此后aux开头的表表示辅助表），用于记录某个词在某一年的总频次。优化后，原过程第4步可以极大简化，简化后的运行图如下：

![pmi_without_rdd](/Users/wuxian/Documents/计算语言所/DiachronicCorpus/sql_explain/pmi_without_rdd.png)

这一步的性能问题主要在group by上。因为group by的两个键分别是第二张WordInvertedIndex的token和最后一张Document的date，因此无法预先索引，运行效率非常低，所以考虑在倒排索引表中添加一个冗余字段rdd_date（此后rdd开头的字段表示冗余字段），并添加联合索引(token, rdd_date)。优化后，第2步涉及的代码得到极大简化。优化后运行图如下：

![pmi_with_rdd_date](/Users/wuxian/Documents/计算语言所/DiachronicCorpus/sql_explain/pmi_with_rdd_date.png)

可以看到虽然解决了多表join的问题，但是并没有命中上一步中建立的索引，依然导致了Full Table Scan。查资料后了解到应该是JOIN后的表并没有引起SQL引擎对索引的优化，现在这一步是最大的性能陷阱，后续将进一步考虑如何解决这个问题。

### Normalized PMI

因为直接返回的PMI结果不利于进行直观的比较，因此考虑采用其衍生指标，Normalized PMI。
$$
npmi \equiv \frac{pmi}{-\log p(x,y)} = \frac{\log[ p(x) p(y)]}{\log p(x,y)} - 1.
$$
npmi将pmi归一化至-1到1之间，-1表示不共现（完全不相关），1表示完全共现（相关），0表示随机共现。

### 小结

在经过上述优化后，针对不同词语的PMI运算速度差异很大。大部分词语在8秒内会完成，少部分词语在20秒内或3秒内完成，极少词语（比如“一”这种词）会达到30秒。返回结果将包含共现词、年份、共现词在该年词频、中心词在该年词频、词对在该年词频、以及计算出的PMI。

## 通信方案

通信采用前后端分离的架构，前端向后端服务器发起数据请求，后端解析请求并翻译成sql语句，使用相应数据库引擎向数据库提交运算，得到结果后进行整理，并返还前端。

通信协议采用异步通信，json格式。

## 展示方案

展示方案目前提供了两种。

### 按年份查看npmi

一种重点展示某一年里，top K个词语的npmi值，并提供切换年份的功能。（此处K取了30）

切换年份是利用一个滑块，拖动来查看不同年份，在后面的DEMO中可以看到。

![按年份查看](/Users/wuxian/Documents/计算语言所/DiachronicCorpus/按年份查看.png)

### top K npmi词语随年份变化

另一种是重点展示随时间变化，一些词从top K变成不是top K（或者反过来）的变化。

大概统计了一下，在10年间，PMI在前50的词语，去掉重复的，大概不到200个，一些含义稳定的词可能只有150个左右。因此考虑把所有词的列出来，然后按照年份展示其持续时间。

这里圆角矩形出现，则表示这个词在这一年位于top K中。矩形宽度没有意义，只是为了让显示连贯；矩形高度表示了这个词的npmi相对大小。

![随年份变化](/Users/wuxian/Documents/计算语言所/DiachronicCorpus/随年份变化.png)

## DEMO

http://162.105.86.202:7070/#/pmi

UI还没有仔细设计，这个版本用于提现功能和数据展示方案。