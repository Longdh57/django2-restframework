# Generated by Django 2.2.7 on 2019-12-17 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_auto_20191129_1120'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shop',
            options={'default_permissions': (), 'ordering': ('-created_date',), 'permissions': (('shop_list_data', 'Can get shop list data'), ('shop_list_search', 'Can get shop list search'), ('shop_detail', 'Can get shop detail'), ('shop_create', 'Can create shop'), ('shop_edit', 'Can edit shop'), ('shop_import', 'Can import data shop'), ('shop_export', 'Can export data shop'))},
        ),
    ]
