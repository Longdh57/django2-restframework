# Generated by Django 2.2.7 on 2019-12-05 11:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('terminal', '0003_terminal_shop'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='terminal',
            options={'default_permissions': (), 'ordering': ['-created_date']},
        ),
    ]