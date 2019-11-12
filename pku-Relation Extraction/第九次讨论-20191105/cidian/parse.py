import json
from bs4 import BeautifulSoup
import re
import os
import datetime

# 为了提取出带有标号的词义释义
number_pattern = r'(\d+\.|①|②|③|④|⑤|\(\d+\)\.|\(\d+\))'
expl_pattern = rf'{number_pattern}?(.*)'
# 终止符号
term_pattern = r'(。$|。"|。”|。|$)'
# 句子的提取模式
sent_pattern = rf'(.*?{term_pattern})'
# 英文的提取模式，形如“[eat]吃”
eng_pattern = r'(\[([A-Za-z\';,\. -]+)\][:∶]?)'

def worker(filename):
    print(datetime.datetime.now(), filename)
    with open('mid1/{}'.format(filename.split('/')[-1]), 'w', buffering=1) as of:
        words = [json.loads(line) for line in open(filename)]
        for word in words:
            # 基本的结构化数据对象
            item = {'word': word['word'], 'jbjs': [], 'xxjs': []}

            # 把存储的html解析成BeautifulSoup对象
            jbjs = BeautifulSoup(word['jbjs'], 'lxml')
            xxjs = BeautifulSoup(word['xxjs'], 'lxml')
            # 提取出内部的文字内容
            if jbjs.p:
                jbjs = jbjs.p.text
            else:
                jbjs = ''
            if xxjs.p:
                xxjs = xxjs.p.text
            else:
                xxjs = ''

            # 先按行切分开，认为一行对应一个词义。
            for line in jbjs.split('\n'):
                line = line.strip().strip('\r')
                if not line:
                    continue
                sense = ''
                examples = []
                # 按句子切分开
                for sent, _ in re.findall(sent_pattern, line):
                    sent = sent.strip()
                    # 认为冒号后面是例句/例词，冒号前面是释义
                    if '：' in sent or ':' in sent:
                        a, b = re.split(':|：', sent, 1)
                        examples.extend(re.split('\||｜', b))
                        # 如果句子中存在书名号，一般是其来源，抛弃不用
                        if '《' in sent and '》' in a:
                            continue
                        else:
                            sense += re.match(expl_pattern, a).group(2)
                    else:
                        sense += re.search(expl_pattern, sent).group(2)
                item['jbjs'].append({'sense': sense.strip(), 'examples': examples})

            # 同样，按行切分开
            for line in xxjs.split('\n'):
                line = line.strip().strip('\r')
                if not line:
                    continue
                sense = ''
                examples = []
                eng = []
                # 按句子切分开
                for sent, _ in re.findall(sent_pattern, line):
                    sent = re.match(expl_pattern, sent).group(2).strip()
                    if not sent:
                        continue
                    # 提取出英语翻译
                    m = re.match(rf'{eng_pattern}?(.*)', sent).groups()
                    if m[1]:
                        eng.extend(m[1].split(';'))
                    sent = m[2]
                    # 与基本解释中同样的处理逻辑
                    if '：' in sent or ':' in sent:
                        a, b = re.split(':|：', sent, 1)
                        examples.extend(re.split('\||｜', b))
                        if '《' in sent and '》' in a:
                            continue
                        else:
                            sense += a
                    elif word['word'] in sent:
                        examples.extend(re.split('\||｜', sent))
                    else:
                        sense += sent
                item['xxjs'].append({'sense': sense.strip(), 'examples': examples, 'eng': eng})
            print(json.dumps(item, ensure_ascii=False, indent=2), file=of)


if __name__ == '__main__':
#     worker('data/append.lined_json')
    # 可以写成并行的，但是速度挺快的，就没写
    for a, b, c in os.walk('data/'):
        for cc in c:
            worker(os.path.join(a, cc))
