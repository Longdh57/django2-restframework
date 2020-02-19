# Generated by Django 2.1.5 on 2019-07-22 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MidTidShop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant_code', models.CharField(blank=True, max_length=255, null=True)),
                ('merchant_name', models.CharField(blank=True, max_length=255, null=True)),
                ('terminal_id', models.CharField(blank=True, max_length=255, null=True)),
                ('terminal_name', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_id', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'mid_tid_shop',
                'ordering': ('shop_id',),
            },
        ),
        migrations.CreateModel(
            name='ShopList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shop_id', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_province_code', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_province_name', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_district_code', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_district_name', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_ward_code', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_ward_name', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_area', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_address', models.CharField(blank=True, max_length=255, null=True)),
                ('merchant_code', models.CharField(blank=True, max_length=255, null=True)),
                ('merchant_brand', models.CharField(blank=True, max_length=255, null=True)),
                ('department_name', models.CharField(blank=True, max_length=255, null=True)),
                ('sale_name', models.CharField(blank=True, max_length=255, null=True)),
                ('sale_email', models.CharField(blank=True, max_length=255, null=True)),
                ('merchant_group_bussiness_type', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(blank=True, max_length=255, null=True)),
                ('shop_created_date', models.DateField()),
            ],
            options={
                'db_table': 'shop_list',
                'ordering': ('shop_id',),
            },
        ),
    ]