# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-13 13:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Grades', '0003_course_module_ed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Criterion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.CharField(max_length=32)),
                ('role', models.CharField(max_length=32)),
                ('module_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Module_ed')),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Study')),
            ],
        ),
        migrations.CreateModel(
            name='Studying',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=32)),
                ('module_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Module_ed')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Student')),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Study')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Course')),
            ],
        ),
    ]
