# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-17 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170315_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='globalfile',
            name='file_type',
            field=models.CharField(choices=[('attachment', 'Attachment'), ('matter_contract', 'Matter Contract'), ('matter_deed', 'Matter Deed'), ('matter_notice', 'Matter Notice'), ('matter_letter', 'Matter Letter')], max_length=32),
        ),
    ]
