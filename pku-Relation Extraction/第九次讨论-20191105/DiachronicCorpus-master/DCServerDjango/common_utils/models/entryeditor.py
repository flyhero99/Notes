from django.db import models
from jsonfield import JSONField

from .common import User


class EntryEditor(models.Model):
    STATUS = (
        ('UNINITIALIZED', '未初始化'),
        ('NORMAL', '正常'),
        ('MERGING', '合并中')
    )

    name = models.CharField(max_length=32, verbose_name='标题')
    word = models.CharField(max_length=32, verbose_name='词条名', default='')
    cells = JSONField(verbose_name='内容', default=[])
    status = models.CharField(max_length=32, choices=STATUS, default='NORMAL')
    is_public = models.BooleanField(verbose_name='是否公开', default=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    kernel_id = models.UUIDField(verbose_name='内核id', null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class EntryEditorCheckpoint(models.Model):
    name_bak = models.CharField(max_length=32, verbose_name='标题')
    word_bak = models.CharField(max_length=32, verbose_name='词条名', default='')
    cells_bak = JSONField(verbose_name='内容', default=[])
    status_bak = models.CharField(max_length=32, choices=EntryEditor.STATUS, default='NORMAL')
    entryeditor = models.ForeignKey(EntryEditor, on_delete=models.CASCADE, related_name='checkpoints')

    created_at = models.DateTimeField(auto_now_add=True)


class EntryEditorFork(models.Model):
    parent = models.ForeignKey(EntryEditor, on_delete=models.CASCADE, related_name='parents')
    child = models.ForeignKey(EntryEditor, on_delete=models.CASCADE, related_name='children')
