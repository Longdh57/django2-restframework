# Generated by Django 2.2.7 on 2019-11-06 10:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='merchant',
            name='merchant_type',
            field=models.IntegerField(help_text='Equivalent with qr_merchant.merchant_type', null=True),
        ),
    ]