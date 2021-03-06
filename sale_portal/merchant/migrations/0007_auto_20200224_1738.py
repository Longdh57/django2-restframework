# Generated by Django 2.2.7 on 2020-02-24 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchant', '0006_auto_20191218_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='merchant',
            name='district_code',
            field=models.CharField(help_text='Equivalent with qr_terminal.district_code', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='merchant',
            name='province_code',
            field=models.CharField(help_text='Equivalent with qr_terminal.province_code', max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='merchant',
            name='wards_code',
            field=models.CharField(help_text='Equivalent with qr_terminal.wards_code', max_length=10, null=True),
        ),
    ]
