import json
import os
import re
import copy

# 这个是因为前面按行写入json的时候不小心加了indent=2的参数，导致一个dict被拆成了多行，所以要手动收集一下
def load_lined_json(filename):
    buff = ''
    for line in open(filename):
        line = line.strip('\n')
        if buff and line == '{':
            yield json.loads(buff)
            buff = '{'
        else:
            buff += line.strip()
    if buff:
        yield json.loads(buff)


# 把所有词语的读进来
data = []
for a, b, c in os.walk('mid1'):
    for cc in c:
        data.extend(list(load_lined_json(os.path.join(a, cc))))

mid2 = []
for d in data:
    nd = {'word': d['word'], 'jbjs': [], 'xxjs': []}
    for js in d['jbjs']:
        if not js['sense']:
            # 如果出现了不存在释义的例子，那么认为这些例子是属于上一个释义的
            if not nd['jbjs']:
                nd['jbjs'].append({'sense': ''.join(js['examples']), 'examples': []})
            else:
                nd['jbjs'][-1]['examples'].extend(js['examples'])
        else:
            nd['jbjs'].append(js)
    for js in d['xxjs']:
        if not js['sense']:
            # 如果出现了不存在释义的例子，那么认为这些例子是属于上一个释义的
            if not nd['xxjs']:
                nd['xxjs'].append({'sense': ''.join(js['examples']), 'examples': [], 'eng': js['eng']})
            else:
                nd['xxjs'][-1]['examples'].extend(js['examples'])
                nd['xxjs'][-1]['eng'].extend(js['eng'])
        else:
            nd['xxjs'].append(js)
    mid2.append(nd)

json.dump(mid2, open('mid2.json', 'w'), ensure_ascii=False, indent=2)

mid3 = copy.deepcopy(mid2)

# 有两种参考的样子
# 第一种类似于：见”膨胀“
# 第二种类似于：犹膨胀
quote_pattern_l = r'("|“|\'|‘)'
quote_pattern_r = r'("|”|\'|‘)'
syno_pattern1 = rf'(亦称|亦作|见|亦指){quote_pattern_l}(.*?){quote_pattern_r}(、{quote_pattern_l}(.*?){quote_pattern_r})?$'
syno_pattern2 = rf'(犹指|犹言|犹)(.*?)$'

term_pattern = r'(。$|。"|。”|。|$)'
sent_pattern = rf'(.*?{term_pattern})'

for d in mid3:
    for js in d['jbjs']+d['xxjs']:
        js['ref'] = []
        for sent, _ in re.findall(sent_pattern, js['sense']):
            # 同样，如果包含书名号，则不认为是参考，而是来源
            if '《' not in sent:
                # 上面的两种例子有时有句号有时没有，匹配时索性都删除掉
                sent = sent.strip().strip('。')
                ret = re.match(syno_pattern1, sent)
                # 如果匹配到了第一种参考
                if ret:
                    new_syn.add((d['word'], sent, ret.group(3).strip()))
                    js['ref'].extend(re.split(r'，|,|;|；', ret.group(3).strip()))
                    # 这种情况发生在存在多个参考，比如：亦作“风花雪月”、“雪月风花”。其中的后者将会匹配到group(7)中
                    if ret.group(7) is not None:
                        new_syn.add((d['word'], sent, ret.group(7).strip()))
                        js['ref'].extend(re.split(r'，|,|;|；', ret.group(7).strip()))
                else:
                    ret = re.match(syno_pattern2, sent.strip())
                    if ret:
                        new_syn.add((d['word'], sent, ret.group(2).strip()))
                        js['ref'].extend(re.split(r'，|,|;|；', ret.group(2).strip()))
        # 把例词例句中的波浪号替换回来
        examples = list(map(lambda x: re.sub('~|～', d['word'], x), js['examples']))
        js['examples'] = []
        # 把连成一串的例词拆分开
        for e in examples:
            js['examples'].extend(re.split('ㄧ|-|丨', e))

json.dump(mid3, open('mid3.json', 'w'), ensure_ascii=False, indent=2)
