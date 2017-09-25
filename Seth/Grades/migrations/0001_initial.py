# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-25 15:07
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coordinator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mc_assistant', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default='', max_length=16)),
                ('code_extension', models.CharField(default='', max_length=16)),
                ('name', models.CharField(max_length=32, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Criterion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('condition', models.CharField(max_length=32)),
                ('role', models.CharField(max_length=32)),
            ],
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0))),
                ('description', models.CharField(max_length=256, null=True)),
                ('grade', models.DecimalField(decimal_places=3, default=1.0, max_digits=6)),
                ('released', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('module_code', models.CharField(max_length=16, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=32)),
                ('start', models.DateField(default=datetime.date(1, 1, 1))),
                ('stop', models.DateField(default=datetime.date(9999, 12, 31))),
            ],
        ),
        migrations.CreateModel(
            name='Module_ed',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.DateField(default=django.utils.timezone.now)),
                ('module_code_extension', models.CharField(default='', max_length=16)),
                ('start', models.DateField(default=datetime.date(1, 1, 1))),
                ('stop', models.DateField(default=datetime.date(9999, 12, 31))),
                ('courses', models.ManyToManyField(to='Grades.Course')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Module')),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('id_prefix', models.CharField(max_length=8)),
                ('person_id', models.CharField(max_length=16)),
                ('start', models.DateField(default=datetime.date(1, 1, 1))),
                ('stop', models.DateField(default=datetime.date(9999, 12, 31))),
                ('role', models.CharField(choices=[('T', 'Teacher'), ('S', 'Student'), ('A', 'Teaching Assistant'), ('V', 'Study Advisor')], max_length=1)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('short_name', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=32, null=True)),
                ('advisors', models.ManyToManyField(to='Grades.Person')),
                ('modules', models.ManyToManyField(to='Grades.Module')),
            ],
        ),
        migrations.CreateModel(
            name='Studying',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=32)),
                ('module_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Module_ed')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Person')),
                ('study', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Study')),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, null=True)),
                ('_type', models.CharField(choices=[('E', 'Exam'), ('A', 'Assignment'), ('P', 'Project')], max_length=1)),
                ('time', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0))),
                ('maximum_grade', models.DecimalField(decimal_places=3, default=10.0, max_digits=6)),
                ('minimum_grade', models.DecimalField(decimal_places=3, default=1.0, max_digits=6)),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Course')),
            ],
        ),
        migrations.AddField(
            model_name='module_ed',
            name='module_coordinator',
            field=models.ManyToManyField(through='Grades.Coordinator', to='Grades.Person'),
        ),
        migrations.AddField(
            model_name='grade',
            name='student_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Submitter', to='Grades.Person'),
        ),
        migrations.AddField(
            model_name='grade',
            name='teacher_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Correcter', to='Grades.Person'),
        ),
        migrations.AddField(
            model_name='grade',
            name='test_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Test'),
        ),
        migrations.AddField(
            model_name='criterion',
            name='module_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Module_ed'),
        ),
        migrations.AddField(
            model_name='criterion',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Study'),
        ),
        migrations.AddField(
            model_name='course',
            name='teachers',
            field=models.ManyToManyField(to='Grades.Person'),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Module_ed'),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Person'),
        ),
    ]
