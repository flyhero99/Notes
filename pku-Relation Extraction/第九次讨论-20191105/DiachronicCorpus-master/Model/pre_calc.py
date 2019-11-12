import sys
import os

import IPython

sys.path.insert(0, os.getcwd())
from DCServer import CalcService
from Model import db, sql_execute

sql = '''select word, sum(count) as cnt from aux_word_pos_count where tag not in ('w', 'm', 'x', 't')
group by word
'''

with db.cursor() as cursor:
    sql_execute(cursor, sql)
    results = cursor.fetchall()

print(len(results))
results = list(filter(lambda x: x['cnt'] >= 100, results))
print(len(results))

# IPython.embed()
# quit()

for i, result in enumerate(results):
    try:
        print(i, result, i/len(results))
        df = CalcService.get_npmi(result['word'])
        # if df.shape[0] < 240:
        #     print(df.shape[0])
        #     CalcService.get_npmi(result['token'], force_refresh=True)
        #     print(result, i, len(results), df.shape[0])
    except Exception as e:
        print(e)
