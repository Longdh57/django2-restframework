# Generated by Django 2.2.7 on 2020-02-11 10:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('area', '0002_area_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='area',
            options={'default_permissions': (), 'ordering': ['code'], 'permissions': (('area_list_data', 'Can get area list data'), ('area_detail', 'Can get area detail'), ('area_create', 'Can create area'), ('area_edit', 'Can edit area'))},
        ),
    ]
