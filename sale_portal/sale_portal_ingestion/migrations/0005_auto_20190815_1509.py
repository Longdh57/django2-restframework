# Generated by Django 2.1.5 on 2019-08-15 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sale_portal_ingestion', '0004_auto_20190815_1459'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='midtidshop',
            options={'default_permissions': (), 'ordering': ('shop_id',)},
        ),
    ]