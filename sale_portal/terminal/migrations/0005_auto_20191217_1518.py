# Generated by Django 2.2.7 on 2019-12-17 15:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terminal', '0004_auto_20191205_1112'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='terminal',
            options={'default_permissions': (('terminal_list_data', 'Can get terminal list data'), ('terminal_list_search', 'Can get terminal list search'), ('terminal_detail', 'Can get terminal detail'), ('terminal_edit', 'Can edit terminal'), ('terminal_export', 'Can export data terminal')), 'ordering': ['-created_date']},
        ),
    ]
