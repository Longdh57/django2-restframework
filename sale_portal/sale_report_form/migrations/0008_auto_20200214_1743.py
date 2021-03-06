# Generated by Django 2.2.7 on 2020-02-14 17:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sale_report_form', '0007_auto_20200211_1101'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='salereport',
            options={'default_permissions': (), 'ordering': ['-created_date'], 'permissions': (('report_list_data', 'Can get sale report list data'), ('report_detail_data', 'Can get sale report detail data'), ('create_sale_report', 'Can create sale report'), ('report_statistic_list_data', 'Can get list sale report statistic'), ('report_statistic__export_data', 'Can export list sale report statistic'))},
        ),
    ]
