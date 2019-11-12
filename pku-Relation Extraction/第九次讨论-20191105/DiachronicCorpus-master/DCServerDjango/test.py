import json
from similarity.qgram import QGram
import cProfile

def calc_cost(cell1, cell2):
    def gen_profile(cell):
        delim = '@' * (FACTOR-1)
        return delim.join(map(json.dumps, map(lambda x: cell.get(x, ''), ['out', 'in', 'style'])))
    FACTOR = 3
    q = QGram(3)
    s1 = gen_profile(cell1)
    s2 = gen_profile(cell2)
    if s1 == s2:
        print('same')
        return 0.0
    distance = q.distance(s1, s2)
    return FACTOR * distance / (len(s1) + len(s2) - 2)


def min_edit_distance_cells(cells1, cells2):
    len1, len2 = len(cells1), len(cells2)
    dp = []
    prev = []
    for _ in range(len1+1):
        dp.append([0] * (len2+1))
        prev.append([(None, None, None)] * (len2+1))
    for i in range(0, len1+1):
        dp[i][0] = i
    for i in range(0, len2+1):
        dp[0][i] = i
    for i, c1 in enumerate(cells1, start=1):
        for j, c2 in enumerate(cells2, start=1):
            cost = calc_cost(c1, c2)
            _prev = [(i-1, j, 'd'), (i, j-1, 'a'), (i-1, j-1, 'm' if cost == 0 else 's')]
            _dp = [dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1] + cost]
            k = min(range(len(_dp)), key=_dp.__getitem__)
            dp[i][j] = _dp[k]
            prev[i][j] = _prev[k]
    now = (len1, len2)
    path = []
    while now != (None, None, None):
        path.append(now)
        now = prev[now[0]][now[1]]
    path = path[::-1]
    return dp[len1][len2], path

def test():
    return min_edit_distance_cells(cells1, cells2)

if __name__=='__main__':
    cells1 = json.load(open('cells1.json'))
    cells2 = json.load(open('cells2.json'))
    cProfile.run('test()')
