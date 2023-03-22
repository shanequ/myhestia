# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-11 17:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matters', '0002_auto_20170301_2202'),
    ]

    operations = [
        migrations.AddField(
            model_name='matterrecord',
            name='solicitor_email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='matterrecord',
            name='solicitor_mobile',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
        migrations.AddField(
            model_name='matterrecord',
            name='solicitor_name',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]