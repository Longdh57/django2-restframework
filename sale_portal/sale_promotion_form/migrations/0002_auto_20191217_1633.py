# Generated by Django 2.2.7 on 2019-12-17 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sale_promotion_form', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salepromotion',
            options={'default_permissions': (), 'ordering': ['-id'], 'permissions': (('sale_promotion_list_data', 'Can get sale_promotion list data'), ('sale_promotion_detail', 'Can get sale_promotion detail'), ('sale_promotion_import', 'Can import sale_promotion'), ('sale_promotion_edit', 'Can edit sale_promotion'), ('sale_promotion_export', 'Can export data sale_promotion'))},
        ),
    ]
