# Generated by Django 2.2.7 on 2020-03-27 09:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_auto_20200324_1524'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shop',
            options={'default_permissions': (), 'ordering': ('-created_date',), 'permissions': (('shop_list_data', 'Can get shop list data'), ('shop_recommend_data', 'Can get  shop recommend data when create merchant report'), ('shop_detail', 'Can get shop detail'), ('shop_create', 'Can create shop'), ('shop_edit', 'Can edit shop'), ('shop_import', 'Can import data shop'), ('shop_export', 'Can export data shop'), ('dashboard_shop_count', 'Can get shop data for dashboard'), ('shop_assign', 'Can assign terminal to shop'), ('shop_create_from_ter', 'Can create shop from terminal'), ('filter_by_cross_assign_status', 'Can filter by cross_assign_status'))},
        ),
    ]