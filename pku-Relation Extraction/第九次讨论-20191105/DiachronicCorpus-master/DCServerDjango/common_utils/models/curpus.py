from django.db import models


# Create your models here.
class Document(models.Model):
    id = models.IntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=15, blank=True, null=True)
    path = models.CharField(max_length=192, blank=True, null=True)

    class Meta:
        db_table = 'Document'


class Sentence(models.Model):
    id = models.IntegerField(primary_key=True)
    content = models.TextField(blank=True, null=True)
    part_of_speech = models.TextField(blank=True, null=True)
    pos = models.IntegerField(blank=True, null=True)
    document = models.ForeignKey(Document, db_column='fk_document_id', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'Sentence'


class PosInvertedIndex(models.Model):
    id = models.IntegerField(primary_key=True)
    token = models.CharField(max_length=10, blank=True, null=True)
    start_offset = models.IntegerField(blank=True, null=True)
    end_offset = models.IntegerField(blank=True, null=True)
    pos = models.IntegerField(blank=True, null=True)
    sentence = models.ForeignKey(Sentence, db_column='fk_sentence_id', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'PosInvertedIndex'


class SenseInvertedIndex(models.Model):
    id = models.IntegerField(primary_key=True)
    token = models.CharField(max_length=20, blank=True, null=True)
    start_offset = models.IntegerField(blank=True, null=True)
    end_offset = models.IntegerField(blank=True, null=True)
    pos = models.IntegerField(blank=True, null=True)
    sentence = models.ForeignKey(Sentence, db_column='fk_sentence_id', on_delete=models.DO_NOTHING)
    rdd_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'SenseInvertedIndex'


class WordInvertedIndex(models.Model):
    id = models.IntegerField(primary_key=True)
    token = models.CharField(max_length=20, blank=True, null=True)
    start_offset = models.IntegerField(blank=True, null=True)
    end_offset = models.IntegerField(blank=True, null=True)
    pos = models.IntegerField(blank=True, null=True)
    sentence = models.ForeignKey(Sentence, db_column='fk_sentence_id', on_delete=models.DO_NOTHING)
    rdd_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = 'WordInvertedIndex'


class AuxPosCount(models.Model):
    token = models.CharField(max_length=10)
    date = models.DateField()
    count = models.BigIntegerField()

    class Meta:
        db_table = 'aux_pos_count'
        unique_together = (('token', 'date'),)


class AuxWordCount(models.Model):
    token = models.CharField(max_length=20)
    date = models.DateField()
    count = models.BigIntegerField()

    class Meta:
        db_table = 'aux_word_count'
        unique_together = (('token', 'date'),)


class AuxWordPosCount(models.Model):
    word = models.CharField(max_length=20)
    tag = models.CharField(max_length=10)
    date = models.DateField()
    count = models.BigIntegerField()

    class Meta:
        db_table = 'aux_word_pos_count'
        unique_together = (('word', 'tag', 'date'),)
