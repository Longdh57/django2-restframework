# Generated by Django 2.2.7 on 2020-02-12 14:35

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0007_auto_20200120_1714'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='shop',
            index=django.contrib.postgres.indexes.GinIndex(fields=['document'], name='shop_documen_74a4cf_gin'),
        ),
    ]
