# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-02 15:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sms',
            name='sms_text',
            field=models.TextField(),
        ),
    ]
