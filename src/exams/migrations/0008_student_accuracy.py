# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-12-16 11:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0007_auto_20161209_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='accuracy',
            field=models.FloatField(default=0.0),
            preserve_default=False,
        ),
    ]