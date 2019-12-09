# Generated by Django 2.2.7 on 2019-12-06 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0005_auto_20191129_1120'),
        ('terminal', '0004_auto_20191205_1112'),
        ('staff', '0003_auto_20191113_0921'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalePromotionTitle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'sale_promotion_title',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='SalePromotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_person', models.CharField(help_text='contact_person', max_length=100, null=True)),
                ('contact_phone_number', models.CharField(help_text='contact_phone_number', max_length=20, null=True)),
                ('contact_email', models.CharField(help_text='contact_email', max_length=100, null=True)),
                ('tentcard_ctkm', models.BooleanField(default=False)),
                ('wobbler_ctkm', models.BooleanField(default=False)),
                ('status', models.IntegerField(choices=[(0, 'Chưa triển khai'), (1, 'Không tìm thấy địa chỉ'), (2, 'Cửa hàng ngừng KD/Đã chuyển địa điểm'), (3, 'Đã triển khai')], default=0)),
                ('image', models.ImageField(blank=True, help_text='Anh nghiem thu', upload_to='sale_promotion_form')),
                ('sub_image', models.ImageField(blank=True, help_text='Anh nghiem thu (ảnh phụ)', upload_to='sale_promotion_form')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('shop', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='shop.Shop')),
                ('staff', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.Staff')),
                ('terminal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='terminal.Terminal')),
                ('title', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sale_promotion_form.SalePromotionTitle')),
            ],
            options={
                'db_table': 'sale_promotion_form',
                'ordering': ['-id'],
                'default_permissions': (),
            },
        ),
    ]