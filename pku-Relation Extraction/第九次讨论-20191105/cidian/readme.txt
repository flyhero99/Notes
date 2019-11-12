cidian.py: 爬虫主程序，将下载的内容放在data中
parse.py: 进行第一步解析，将网页解析成结构化数据放在mid1中
post_process.py: 后处理，分两步进行。第一步解决一些解析时的格式错误，放在mid2中；第二步进行进一步结构化，放在mid3中。
append.py: 补充一些遗漏的词语。这一步应该在爬虫之后运行。


data/: 下载下来的原始数据
mid1/: 进行了初步解析，结构化数据
mid2.json: 后处理，合并了分离的sense和examples
mid3.json: 后处理，提取出了参考引用，规范化了examples
