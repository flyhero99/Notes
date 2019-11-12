from django.db import models
from jsonfield import JSONField

from .common import User


class Notebook(models.Model):
    name = models.CharField(max_length=32, verbose_name='标题')
    cells = JSONField(verbose_name='内容', default='[]')
    is_public = models.BooleanField(verbose_name='是否公开', default=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    kernel_id = models.UUIDField(verbose_name='内核id', null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

