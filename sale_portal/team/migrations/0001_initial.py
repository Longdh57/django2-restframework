# Generated by Django 2.2.7 on 2019-11-08 09:45

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=20, null=True, unique=True)),
                ('description', models.TextField(null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'team',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='TeamLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('old_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('new_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('team_id', models.IntegerField(blank=True, null=True)),
                ('type', models.IntegerField(choices=[(0, 'Created new Team'), (1, 'Deleted Team'), (2, 'Updated Team')])),
                ('created_date', models.DateTimeField(auto_now_add=True, null=True)),
            ],
            options={
                'db_table': 'team_log',
                'default_permissions': (),
            },
        ),
    ]
