# 将原文档以句子为单位进行切分
class CutSent:
    r_cut_delim = "。！？…"  # ”
    l_cut_delim = ""  # “

    @classmethod
    def cut(cls, sent):
        def push_buff(c=None):
            if buff[0]:
                if c:
                    buff[0] += c
                ret.append(buff[0])
                buff[0] = ''
            else:
                if ret and c:
                    ret[-1] += c

        ret = []
        buff = ['']
        for c in sent:
            if c in cls.r_cut_delim:
                push_buff(c)
            elif c in cls.l_cut_delim:
                push_buff()
                buff[0] += c
            elif c == '”':
                if not buff[0] and ret:
                    ret[-1] += c
                elif buff[0]:
                    buff[0] += c
            else:
                buff[0] += c
        push_buff()
        return ret

    @classmethod
    def cut_pos(cls, line):
        sents = cls.cut(''.join([x.split('/')[0] for x in line.split()]))
        pos = line.split()
        ret = []
        buff = []
        i = 0
        for sent in sents:
            cnt = 0
            while cnt < len(sent):
                cnt += len(pos[i].split('/')[0])
                buff.append(pos[i])
                i += 1
            ret.append(buff)
            buff = []
        return ret


if __name__ == '__main__':
    line = '晚间/t 八时/t ，/w 毛/n 主席/n 、/w 刘/n 主席/n 等/u 党/n 和/c 国家/n 领导人/n ，/w 同/p 许多/m 战斗/v 英雄/n 、/w 民兵/n 代表/n 和/c 工农业/n ' \
           '劳动模范/n 们/k 一起/s ，/w 登/v 上/v 人民大会堂/n 的/u 主席台/n ，/w 向/p 参加/v 联欢/v 的/u 各族/r 各界/r 人民/n 和/c 部队/n 官兵/n ，/w 致以/v ' \
           '亲切/a 的/u 节日/n 祝贺/v 。/w 这时/r ，/w 全场/n 万众/n 欢腾/v ，/w 热烈/a 高呼/v ：/w “/w 毛/n 主席/n 万岁/n ！/w ”/w “/w 中国/n 共产党/n ' \
           '万岁/n ！/w ”/w 会场/n 上/f ，/w 暴风雨/n 般/u 的/u 掌声/n 持续/v 达/v 数/m 分钟/q 之/u 久/g 。/w '
    # line = ''.join([x.split('/')[0] for x in line.split()])
    # line = '会议对周恩来总理在人大会议上作的“政府工作报告”继续进行了讨论，就即将在三届人大首次会议上提出的国家领导人等候选人名单，和即将在政协四届首次会议上提出的政协领导人候选人名单问题，进行了协商'
    sents = CutSent.cut_pos(line)
    for sent in sents:
        print(sent)
