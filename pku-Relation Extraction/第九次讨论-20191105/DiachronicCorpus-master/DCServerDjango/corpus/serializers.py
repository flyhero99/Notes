from rest_framework import serializers

from common_utils.models import Sentence


class StatisticsSerializer(serializers.Serializer):
    pass


class GetPMISerializer(serializers.Serializer):
    token = serializers.CharField()


class GetPhrasePMISerializer(serializers.Serializer):
    tokens = serializers.JSONField()


class GetTagPMISerializer(serializers.Serializer):
    token = serializers.CharField()
    pos = serializers.CharField()


class GetCountSerializer(serializers.Serializer):
    token = serializers.CharField()


class GetInstanceSerializer(serializers.Serializer):
    token = serializers.CharField()
    date = serializers.CharField()
    page_num = serializers.IntegerField()
    page_size = serializers.IntegerField()
    MAX_LEN = serializers.IntegerField(default=30)


class GetCooccurCountSerializer(serializers.Serializer):
    CO_TABLE = (
        ('word', 'WordInvertedIndex'),
        ('tag', 'PosInvertedIndex')
    )

    src_word = serializers.CharField()
    src_tag = serializers.CharField()
    co_table = serializers.ChoiceField(CO_TABLE)
    co_tag = serializers.CharField()
    date = serializers.CharField()
    pos_range = serializers.JSONField()


class GetCooccurSerializer(serializers.Serializer):
    CO_TABLE = (
        ('word', 'WordInvertedIndex'),
        ('tag', 'PosInvertedIndex')
    )

    table1 = serializers.ChoiceField(CO_TABLE)
    table2 = serializers.ChoiceField(CO_TABLE)
    token1 = serializers.CharField()
    token2 = serializers.CharField()
    date = serializers.CharField()
    pos_range = serializers.JSONField()


class SentenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentence
        fields = '__all__'
