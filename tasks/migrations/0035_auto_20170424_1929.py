# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-04-24 19:29
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0034_auto_20170424_1815'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exporttask',
            name='filenames',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(null=True), default=list, size=None),
        ),
    ]
