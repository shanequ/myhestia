# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-03-17 14:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matters', '0005_auto_20170315_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matterrecord',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='project_matters', to='project.Project'),
        ),
    ]
