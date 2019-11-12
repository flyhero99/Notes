from django.shortcuts import render
from sklearn import preprocessing
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
import numpy as np
import pandas as pd

from common_utils.models import Document, Sentence, WordInvertedIndex
from common_utils.services import CalcService
from corpus import serializers

from Model import PeopleDaily


# Create your views here.
class StatisticsViewSet(viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.StatisticsSerializer

    def get_serializer_class(self):
        return {
            'get_pmi': serializers.GetPMISerializer,
            'get_phrase_pmi': serializers.GetPhrasePMISerializer,
            'get_tag_pmi': serializers.GetTagPMISerializer,
            'get_cooccur_count': serializers.GetCooccurCountSerializer,
            'get_cooccur': serializers.GetCooccurSerializer,
            'get_count': serializers.GetCountSerializer,
            'get_instance': serializers.GetInstanceSerializer
        }.get(self.action, self.serializer_class)

    @action(methods=['POST'], detail=False)
    def get_pmi(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        # 从CalcService得到一个pandas.DataFrame，进行具体业务级的后处理
        df = CalcService.get_npmi(token)
        if df.empty:
            return Response({'detail': '无此词语'}, status=status.HTTP_404_NOT_FOUND)
        # 把时间戳格式的数据转化成年份，下同
        df.date = df.date.map(lambda x: x.strftime('%Y'))
        # 得到涉及到的所有日期和tokens
        dates = df.drop_duplicates('date')['date']
        tokens = df.drop_duplicates('token')['token']

        # 柱状图需要的数据格式，所有值构成一个list
        # 以日期为key，token和npmi的list为value
        data = {}
        bar_data = {}
        for date in dates:
            bar_data[date] = df[df.date == date].loc[:, ['token', 'npmi']].to_dict('list')
        data['bar'] = bar_data

        # 散点图需要的数据格式
        # dates包含所有日期
        # tokens包含所有词条
        # data是横纵坐标与值构成tuple，组成的list
        scatter_data = {}
        scatter_data['dates'] = dates.tolist()
        scatter_data['tokens'] = tokens.tolist()
        scatter_data['data'] = []
        for i in range(len(dates)):
            for j in range(len(tokens)):
                ks = df[(df.date == dates[i]) & (df.token == tokens[j])][['npmi']]
                if not ks.empty:
                    value = ks.values[0][0]
                else:
                    value = 0
                scatter_data['data'].append((i, j, value))
        data['scatter'] = scatter_data

        cloud_data = {}
        cloud_data['dates'] = dates.tolist()
        cloud_data['data'] = []
        cloud_data['links'] = []
        for date in dates:
            d = []
            for record in df[df.date == date][['npmi', 'token']].to_dict('records'):
                tmp = df[(df.date == str(int(date) - 1)) & (df.token == record['token'])]['npmi']
                record['diff'] = record['npmi'] - (0 if tmp.empty else tmp.values[0])
                d.append(record)
            tmp = df[df.date == date].drop_duplicates('token')['token'].tolist()
            cloud_data['data'].append(d)
            cloud_data['links'].append(CalcService.calc_links(tmp))
        data['cloud_data'] = cloud_data

        return Response(data)

    @action(methods=['POST'], detail=False)
    def get_phrase_pmi(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data['tokens']

        df = CalcService.get_phrase_npmi(tokens)
        df.date = df.date.map(lambda x: x.strftime('%Y'))
        dates = df.drop_duplicates('date')['date']
        tokens = df.drop_duplicates('token')['token']

        data = {}
        bar_data = {}
        for date in dates:
            bar_data[date] = df[df.date == date].loc[:, ['token', 'npmi']].to_dict('list')
        data['bar'] = bar_data

        scatter_data = {}
        scatter_data['dates'] = dates.tolist()
        scatter_data['tokens'] = tokens.tolist()
        scatter_data['data'] = []
        for i in range(len(dates)):
            for j in range(len(tokens)):
                ks = df[(df.date == dates[i]) & (df.token == tokens[j])][['npmi']]
                if not ks.empty:
                    value = ks.values[0][0]
                else:
                    value = 0
                scatter_data['data'].append((i, j, value))
        data['scatter'] = scatter_data

        return Response(data)

    @action(methods=['POST'], detail=False)
    def get_tag_pmi(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        pos = serializer.validated_data['pos']

        df = CalcService.get_tag_npmi(token, pos=pos)
        if df.empty:
            return Response({'detail': '无此词语'}, status=status.HTTP_404_NOT_FOUND)
        df.date = df.date.map(lambda x: x.strftime('%Y'))
        src_tags = df.drop_duplicates('src_tag')['src_tag']

        data = {}
        # river_data已弃用
        # river_data = {}
        # for src_tag in src_tags:
        #     sub_df = df[df.src_tag == src_tag]
        #     co_tags = sub_df.drop_duplicates('co_tag')['co_tag'].tolist()
        #
        #     river_data[src_tag] = sub_df.loc[:, ['date', 'npmi', 'co_tag']].to_dict('split')
        #     river_data[src_tag]['co_tags'] = co_tags
        # data['river_data'] = river_data

        # 柱状图，与上文描述的格式类似
        bar_data = {}
        years = Document.objects.values('date__year').distinct()
        tags = ['n', 'v', 'u', 'd', 'm', 'p', 'a', 'r', 'q', 'c', 't', 'g', 'f', 'b', 'l', 's', 'x', 'y', 'k', 'z',
                'o', 'e', 'h', '一', 'n_newword', 'url', 'w']
        year2idx = {str(k['date__year']): v for v, k in enumerate(years)}
        tag2idx = {k: v for v, k in enumerate(tags)}
        bar_data['years'] = years
        bar_data['tags'] = tags
        bar_data['data'] = {}
        for src_tag in src_tags:
            sub_df = df[df.src_tag == src_tag]
            a = np.zeros((len(tags), len(years)))
            for i in sub_df.itertuples():
                a[tag2idx[i.co_tag], year2idx[i.date]] = i.pmi
            na = preprocessing.normalize(a, norm='l1', axis=0)
            bar_data['data'][src_tag] = na.tolist()
        data['bar_data'] = bar_data

        return Response(data)

    @action(methods=['POST'], detail=False)
    def get_cooccur_count(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        table = {'word': 'WordInvertedIndex', 'tag': 'PosInvertedIndex'}
        params = serializer.validated_data
        params['co_table'] = table[params['co_table']]
        ret = PeopleDaily.get_cooccur_count(**params)
        return Response(ret)

    @action(methods=['POST'], detail=False)
    def get_cooccur(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        table = {'word': 'WordInvertedIndex', 'tag': 'PosInvertedIndex'}
        params = serializer.validated_data
        params['table1'] = table[params['table1']]
        params['table2'] = table[params['table2']]
        ret = PeopleDaily.get_cooccur(**params)
        return Response(ret)

    @action(methods=['POST'], detail=False)
    def get_count(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        params = serializer.validated_data
        ret = PeopleDaily.get_count(params['token'])
        if not ret:
            return Response({'detail': '无此词语'}, status=status.HTTP_404_NOT_FOUND)
        df = pd.DataFrame(ret)
        df.date = df.date.map(lambda x: x.strftime('%Y'))
        return Response(df.to_dict('list'))

    @action(methods=['POST'], detail=False)
    def get_instance(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        params = serializer.validated_data
        MAX_LEN = params['MAX_LEN']

        if params == '*':
            instances = WordInvertedIndex.objects.filter(token=params['token'])[params['page_num'] * params['page_size']: params['page_num'] * params['page_size'] + params['page_size']]
        else:
            instances = WordInvertedIndex.objects.filter(token=params['token'], rdd_date=params['date'])[params['page_num'] * params['page_size']: params['page_num'] * params['page_size'] + params['page_size']]

        ret = []
        for instance in instances:
            ret.append({
                'sentence_id': instance.sentence_id,
                'content': instance.sentence.content,
                'sentence_pos': instance.sentence.pos,
                'fk_document_id': instance.sentence.document_id,
                'so': instance.start_offset,
                'eo': instance.end_offset
            })
        # 为了实现以关键词对齐，将原句分成两部分，并分别补长至MAX_LEN
        for instance in ret:
            # 关键词两边的句子
            left = instance['content'][:instance['eo']]
            right = instance['content'][instance['eo']:]
            # 分别记录两边的句子pos到了哪里
            lpos = instance['sentence_pos']
            rpos = instance['sentence_pos']
            # 当左边长度不够，不断补充句子
            while len(left) < MAX_LEN:
                sentence = Sentence.objects.filter(document=instance['fk_document_id'], pos=lpos - 1)
                lpos -= 1
                if sentence:
                    # 每次补充在原句左边，相应修改关键词偏移量
                    left = sentence[0].content + left
                    instance['so'] += len(sentence[0].content)
                    instance['eo'] += len(sentence[0].content)
                else:
                    break
            # 对右侧的补充，同上
            while len(right) < MAX_LEN:
                sentence = Sentence.objects.filter(document=instance['fk_document_id'], pos=rpos + 1)
                rpos += 1
                if sentence:
                    right += sentence[0].content
                else:
                    break
            # 当左边长度超过了，做截断
            if len(left) > MAX_LEN:
                offset = len(left) - MAX_LEN
                left = left[offset:]
                instance['so'] -= offset
                instance['eo'] -= offset
            instance['left'] = left
            instance['right'] = right[:MAX_LEN]
        return Response(ret)


class SentenceViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.SentenceSerializer
    queryset = Sentence.objects.all()

    @action(methods=['GET'], detail=True)
    def neighbors(self, request, pk=None):
        neighbors = CalcService.get_sentence_neighbors(pk, 10)
        ret = []
        for neighbor in neighbors:
            ret.append(Sentence.objects.get(id=neighbor))
        return Response(serializers.SentenceSerializer(ret, many=True).data)
