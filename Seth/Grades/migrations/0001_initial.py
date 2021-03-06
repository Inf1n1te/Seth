# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-03 16:31
from __future__ import unicode_literals

import Grades.models
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
                ('is_assistant', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['person'],
            },
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
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('grade', models.DecimalField(decimal_places=1, default=1.0, max_digits=4)),
                ('released', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ModuleEdition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module_code', models.CharField(max_length=32)),
                ('year', models.IntegerField(default=Grades.models.getyear)),
                ('block', models.CharField(choices=[('1A', 'Block 1A'), ('1B', 'Block 1B'), ('2A', 'Block 2A'), ('2B', 'Block 2B'), ('3A', 'Block 3A'), ('3B', 'Block 3B'), ('JAAR', 'Block JAAR')], max_length=16)),
            ],
            options={
                'ordering': ['module', '-year', '-block'],
            },
        ),
        migrations.CreateModel(
            name='ModulePart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('module_edition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.ModuleEdition')),
            ],
            options={
                'ordering': ['module_edition', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('university_number', models.CharField(max_length=16, unique=True)),
                ('email', models.EmailField(max_length=254, null=True, verbose_name='Student e-mail')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['university_number'],
            },
        ),
        migrations.CreateModel(
            name='Study',
            fields=[
                ('abbreviation', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('advisers', models.ManyToManyField(blank=True, to='Grades.Person')),
                ('modules', models.ManyToManyField(blank=True, to='Grades.Module')),
            ],
        ),
        migrations.CreateModel(
            name='Studying',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(max_length=32)),
                ('module_edition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.ModuleEdition')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Person')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('T', 'Teacher'), ('A', 'Teaching Assistant')], max_length=1)),
                ('module_part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.ModulePart')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Person')),
            ],
            options={
                'ordering': ['person'],
            },
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('type', models.CharField(choices=[('E', 'Exam'), ('A', 'Assignment'), ('P', 'Project')], max_length=1)),
                ('maximum_grade', models.DecimalField(decimal_places=1, default=10.0, max_digits=4)),
                ('minimum_grade', models.DecimalField(decimal_places=1, default=1.0, max_digits=4)),
                ('released', models.BooleanField(default=False)),
                ('module_part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.ModulePart')),
            ],
            options={
                'ordering': ['module_part', '-type', 'id'],
            },
        ),
        migrations.AddField(
            model_name='modulepart',
            name='teachers',
            field=models.ManyToManyField(through='Grades.Teacher', to='Grades.Person'),
        ),
        migrations.AddField(
            model_name='moduleedition',
            name='coordinators',
            field=models.ManyToManyField(blank=True, through='Grades.Coordinator', to='Grades.Person'),
        ),
        migrations.AddField(
            model_name='moduleedition',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Module'),
        ),
        migrations.AddField(
            model_name='grade',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Submitter', to='Grades.Person'),
        ),
        migrations.AddField(
            model_name='grade',
            name='teacher',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Correcter', to='Grades.Person'),
        ),
        migrations.AddField(
            model_name='grade',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Test'),
        ),
        migrations.AddField(
            model_name='criterion',
            name='module_edition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.ModuleEdition'),
        ),
        migrations.AddField(
            model_name='criterion',
            name='study',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Study'),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='module_edition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.ModuleEdition'),
        ),
        migrations.AddField(
            model_name='coordinator',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Grades.Person'),
        ),
        migrations.AlterUniqueTogether(
            name='studying',
            unique_together=set([('person', 'module_edition')]),
        ),
        migrations.AlterUniqueTogether(
            name='moduleedition',
            unique_together=set([('year', 'module', 'block')]),
        ),
    ]
