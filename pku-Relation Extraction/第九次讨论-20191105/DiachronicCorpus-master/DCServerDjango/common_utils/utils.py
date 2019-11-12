import json
from similarity.qgram import QGram


def make_cell(i, o, s, t):
    return {
        'in': i,
        'out': o,
        'style': s,
        'type': t
    }


def make_result_set(object, type):
    return {'data': object, 'type': type}


def merge_cells(cells1, cells2):
    score, path = min_edit_distance_cells(cells1, cells2)
    ret = []
    for p in path[:-1]:
        if p[2] == 'm':
            ret.append({
                'cell': cells1[p[0]],
                'action': 'match'
            })
        elif p[2] == 'd':
            ret.append({
                'cell': cells1[p[0]],
                'action': 'delete'
            })
        elif p[2] == 'a':
            ret.append({
                'cell': cells2[p[1]],
                'action': 'add'
            })
        elif p[2] == 's':
            ret.append({
                'cell1': cells1[p[0]],
                'cell2': cells2[p[1]],
                'action': 'substitute'
            })
        else:
            raise ValueError('Unsupported action: {}'.format(p[2]))
    return ret


def calc_cost(p1, p2):
    def distance_profile(profile0, profile1):
        union = set(profile0.keys())
        union.update(profile1.keys())
        agg = 0
        for k in union:
            v0 = profile0.get(k, 0)
            v1 = profile1.get(k, 0)
            agg += abs(v0 - v1)
        return agg
    FACTOR = 2
    distance = distance_profile(p1, p2)
    return FACTOR * distance / (len(p1) + len(p2) - 4)


def min_edit_distance_cells(cells1, cells2):
    def get_profile(cell, k=3):
        delim = '@' * (k-1)
        src = delim.join(map(json.dumps, map(lambda x: cell.get(x, ''), ['out', 'in', 'style'])))
        shingles = {}
        for i in range(len(src) - k + 1):
            profile = src[i:i + k]
            shingles[str(profile)] = shingles.get(str(profile), 0) + 1
        return shingles
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
    profiles1 = [get_profile(c) for c in cells1]
    profiles2 = [get_profile(c) for c in cells2]
    for i, c1 in enumerate(profiles1, start=1):
        for j, c2 in enumerate(profiles2, start=1):
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
