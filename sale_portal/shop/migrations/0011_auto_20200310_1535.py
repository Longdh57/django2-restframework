# Generated by Django 2.2.7 on 2020-03-10 15:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0010_auto_20200226_1653'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shop',
            options={'default_permissions': (), 'ordering': ('-created_date',), 'permissions': (('shop_list_data', 'Can get shop list data'), ('shop_detail', 'Can get shop detail'), ('shop_create', 'Can create shop'), ('shop_edit', 'Can edit shop'), ('shop_import', 'Can import data shop'), ('shop_export', 'Can export data shop'), ('dashboard_shop_count', 'Can get shop data for dashboard'), ('shop_assign', 'Can create shop from terminal or assign terminal to shop'), ('filter_by_cross_assign_status', 'Can filter by cross_assign_status'))},
        ),
    ]
