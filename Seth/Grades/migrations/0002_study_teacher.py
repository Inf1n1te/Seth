# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-13 13:17
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Grades', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Study',
            fields=[
                ('short_name', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('modules', models.ManyToManyField(to='Grades.Module')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('teacher_id', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Student')),
            ],
        ),
    ]
