# Generated by Django 2.2.7 on 2020-07-01 16:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale_report_form', '0012_auto_20200325_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='salereport',
            name='new_store_image',
            field=models.ImageField(blank=True, help_text='Noi dung mo moi - image cua hang', upload_to='sale_report_form'),
        ),
    ]