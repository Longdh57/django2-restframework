# Generated by Django 2.2.7 on 2019-12-18 15:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0005_auto_20191205_1112'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='merchant',
            options={'default_permissions': (), 'ordering': ['-created_date'], 'permissions': (('merchant_list_data', 'Can get merchant list data'), ('merchant_detail', 'Can get merchant detail'))},
        ),
    ]