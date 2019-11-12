from collections import defaultdict

import IPython
import inspect
import pickle
import re
import redis
import traceback
from django.db.models import Count, F

from .CalcService import CalcClient
from common_utils.models import *

r = redis.Redis('localhost', 6379, 1)
eer = redis.Redis('localhost', 6379, 2)
session_id = 1


###################################################
# kernel管理函数
###################################################


def gen_variable_key(kernel_id, name):
    return '{}:{}'.format(kernel_id, name)


def shutdown_kernel(kernel_id):
    keys = r.keys('{}*'.format(kernel_id))
    for key in keys:
        r.delete(key)
    return {}, 200

###################################################
# kernel命令
###################################################


def make_result_set(object, type):
    return {'data': object, 'type': type}


def freq(pattern, kernel_id):
    results = WordInvertedIndex.objects.filter(token=pattern).values('rdd_date').annotate(count=Count('*'),
                                                                                          date=F('rdd_date'))
    return results.values('date', 'count'), 'ListWithChart'


def sense_freq(word, sense_id, kernel_id):
    results = SenseInvertedIndex.objects.filter(token='{}_s{}'.format(word, sense_id)).values('rdd_date').annotate(
        count=Count('*'), date=F('rdd_date'))
    return results.values('date', 'count'), 'ListWithChart'


def compare(name1, name2, by, kernel_id):
    results1, _ = get(name1, kernel_id)
    results2, _ = get(name2, kernel_id)
    results = defaultdict(dict)
    for result in results1:
        results[result[by]].update({'{}_{}'.format(k, name1): v for k, v in result.items() if k != by})
        results[result[by]].update({by: result[by]})
    for result in results2:
        results[result[by]].update({'{}_{}'.format(k, name2): v for k, v in result.items() if k != by})
        results[result[by]].update({by: result[by]})
    return list(results.values()), 'ListWithChart'


def sense_examples(word, sense_id, year, offset, num, kernel_id):
    offset = int(offset)
    num = int(num)
    instances = Sentence.objects.filter(senseinvertedindex__token='{}_s{}'.format(word, sense_id),
                                        senseinvertedindex__rdd_date='{}-01-01'.format(year))[offset:offset+num]
    return {'contents': instances.values('id', 'content'),  'word': word, 'year': year}, 'ExampleTable'


def synonyms(word, kernel_id):
    with CalcClient() as client:
        ret = client.get_synonyms(word)
        ret = [{'word': r[0], 'similarity': r[1]} for r in ret]
        return ret, 'List'


def multi_synonyms(word, kernel_id):
    with CalcClient() as client:
        ret = client.get_multi_synonyms(word, 10)
        ret = [[{'word': rr[0], 'similarity': rr[1]} for rr in r] for r in ret]
        return ret, 'ListWithList'


def wiki(word, kernel_id):
    ret = {}
    ret['word'] = word
    ret['senses'] = []
    senses, _ = multi_synonyms(word, kernel_id)
    for i, sense in enumerate(senses):
        data = {}
        data['sense_id'] = i + 1
        data['sense'] = '【自动生成】'
        data['synonyms'] = sense
        data['examples'] = []
        for year in range(1986, 1996):
            instances, _ = sense_examples(word, i, year, 0, 5, kernel_id)
            data['examples'].append({'year': year, 'sentences': [ee['content'] for ee in instances]})
        ret['senses'].append(data)
    return ret, 'Wiki'


def show(kernel_id):
    keys = r.keys(gen_variable_key(kernel_id, '*'))
    ret = []
    for key in keys:
        name = b':'.join(key.split(b':')[1:])
        type = pickle.loads(r.get(gen_variable_key(kernel_id, name.decode('utf8')))).get('type', 'UNK')
        ret.append({'var_name': name, 'type': type})
    return ret, 'List'


def get(name, kernel_id):
    ret = r.get(gen_variable_key(kernel_id, name))
    if ret is None:
        raise ValueError('变量{}未定义'.format(name))
    ret = pickle.loads(ret)
    return ret['data'], ret['type']


def save(name, object, kernel_id):
    r.set(gen_variable_key(kernel_id, name), pickle.dumps(object))
    return True, 'Boolean'


def assign(name1, name2, kernel_id):
    data, _type = get(name2, kernel_id)
    return save(name1, make_result_set(data, _type), kernel_id)


patterns = [
    ('^(.*)=(.*)\((.*)\)$', 'groups.group(1)', 'groups.group(2)', 'groups.group(3)'),
    ('^(.*)\((.*)\)$', '"ans"', 'groups.group(1)', 'groups.group(2)'),
    ('^(.*)=(.*)$', '"ans"', '"assign"', '"name1={}, name2={}".format(groups.group(1), groups.group(2))'),
    ('.*', '"ans"', '"get"', '"name={}".format(command)')
]


def parse(command):
    target = None
    func_name = None
    param_str = None
    for pattern in patterns:
        groups = re.match(pattern[0], command)
        if groups is not None:
            target = eval(pattern[1]).strip()
            func_name = eval(pattern[2]).strip()
            param_str = eval(pattern[3]).strip()
            break
    params = {}
    if param_str:
        for param_pair in param_str.split(','):
            tmp = re.match('(.*)=(.*)', param_pair.strip())
            if tmp is None:
                raise ValueError('解析错误：参数应该以name=value的格式给出')
            params[tmp[1].strip()] = tmp[2].strip().strip('"')
    return target, func_name, params


func_list = [show, get, assign, freq, compare, synonyms, wiki, sense_freq, sense_examples, multi_synonyms]
func_map = {k.__name__: k for k in func_list}
func_map.update({})


def execute_command(kernel_id, command):
    if not kernel_id:
        return {'executing_num': '', 'output': {'detail': '请先连接一个内核！'}}, 400
    num = r.get(kernel_id+'.num')
    if num is None:
        num = -1
    num = int(num) + 1
    r.set(kernel_id+'.num', num)
    output = ''
    code = 200
    for single_command in command.split('\n'):
        if single_command == '':
            continue
        output, code = _execute_command(kernel_id, single_command)
        if code != 200:
            break
    ret = {'executing_num': num, 'output': output}
    return ret, code


def _execute_command(kernel_id, command):
    try:
        target, func_name, params = parse(command)
    except Exception as e:
        return {"detail": str(e), "type": "String"}, 500
    if func_name not in func_map:
        return {"detail": "不存在对应的函数名{}".format(func_name), "type": "String"}, 404
    func = func_map[func_name]
    expected_params = set(inspect.getfullargspec(func).args).difference(['kernel_id', 'target'])
    if expected_params != set(params.keys()):
        return {"detail": "函数{}的参数列表不符，期待的输入是({})".format(func_name, ', '.join(expected_params)), "type": "String"}, 400
    try:
        ret, _type = func(**params, kernel_id=kernel_id)
        result_set = make_result_set(ret, _type)
        if target is not None:
            save(target, result_set, kernel_id)
        return result_set, 200
    except Exception as e:
        print(traceback.format_exc())
        return {"detail": str(e), "type": "String"}, 500


if __name__ == '__main__':
    session_id = 1
    name = 'default'
    kernel_id = '5d4929d1a2a24814a44837c732e5c078'
    IPython.embed()
