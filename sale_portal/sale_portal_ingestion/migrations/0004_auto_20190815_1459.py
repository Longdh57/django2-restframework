# Generated by Django 2.1.5 on 2019-08-15 14:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sale_portal_ingestion', '0003_auto_20190723_1524'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shoplist',
            options={'default_permissions': (), 'ordering': ('shop_id',)},
        ),
    ]
