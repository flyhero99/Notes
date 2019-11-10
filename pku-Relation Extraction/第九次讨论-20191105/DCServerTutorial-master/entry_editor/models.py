from django.db import models

# Create your models here.
from django.db import models
from jsonfield import JSONField


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

    kernel_id = models.UUIDField(verbose_name='内核id', null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)