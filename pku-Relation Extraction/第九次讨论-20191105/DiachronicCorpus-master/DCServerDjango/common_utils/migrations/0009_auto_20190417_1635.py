# Generated by Django 2.0.1 on 2019-04-17 16:35

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('common_utils', '0008_entryeditorcheckpoint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entryeditor',
            name='cells',
            field=jsonfield.fields.JSONField(default=[], verbose_name='内容'),
        ),
        migrations.AlterField(
            model_name='entryeditorcheckpoint',
            name='cells_bak',
            field=jsonfield.fields.JSONField(default=[], verbose_name='内容'),
        ),
    ]
