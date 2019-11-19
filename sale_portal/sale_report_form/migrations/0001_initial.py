# Generated by Django 2.2.7 on 2019-11-19 10:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SaleReport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purpose', models.IntegerField(choices=[(0, 'Mở mới'), (1, 'Triển khai'), (2, 'Chăm sóc')], default=0)),
                ('longitude', models.FloatField(null=True)),
                ('latitude', models.FloatField(null=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('updated_date', models.DateTimeField(auto_now=True)),
                ('new_merchant_name', models.CharField(help_text='Noi dung mo moi merchant_name', max_length=255, null=True)),
                ('new_merchant_brand', models.CharField(help_text='Noi dung mo moi merchant_brand', max_length=255, null=True)),
                ('new_address', models.TextField(help_text='Noi dung mo moi address', null=True)),
                ('new_customer_name', models.CharField(help_text='Noi dung mo moi customer_name', max_length=255, null=True)),
                ('new_phone', models.CharField(help_text='Noi dung mo moi phone', max_length=100, null=True)),
                ('new_result', models.IntegerField(blank=True, choices=[(0, 'Dong y, da ky duoc HD'), (1, 'Dong y, chua ky duoc HD'), (2, 'Can xem xet them'), (3, 'Tu choi hop tac')], help_text='Noi dung mo moi result', null=True)),
                ('new_note', models.TextField(help_text='Noi dung ghi chu', null=True)),
                ('shop_code', models.CharField(blank=True, help_text='Relative with shop.code', max_length=100, null=True)),
                ('shop_status', models.IntegerField(blank=True, choices=[(0, 'Da nghi kinh doanh/ khong co cua hang thuc te'), (1, 'Muon thanh ly QR'), (2, 'Dang hoat dong'), (3, 'Không hợp tác'), (4, 'Da chuyen dia diem')], default=0, null=True)),
                ('image_outside', models.ImageField(blank=True, help_text='Noi dung Cham soc - KQ cham soc, Noi dung Trien khai - image_outside', upload_to='sale_report_form')),
                ('image_inside', models.ImageField(blank=True, help_text='Noi dung Cham soc - KQ cham soc, Noi dung Trien khai - image_outside', upload_to='sale_report_form')),
                ('image_store_cashier', models.ImageField(blank=True, help_text='Noi dung Cham soc - KQ cham soc, Noi dung Trien khai - image_store_cashier', upload_to='sale_report_form')),
                ('cessation_of_business_note', models.TextField(help_text='Noi dung Cham soc - Cua hang nghi kinh doanh - note', null=True)),
                ('cessation_of_business_image', models.ImageField(blank=True, help_text='Noi dung Cham soc - Cua hang nghi kinh doanh - image', upload_to='sale_report_form')),
                ('customer_care_posm', models.TextField(help_text='Noi dung Cham soc - KQ cham soc - POSM', null=True)),
                ('customer_care_cashier_reward', models.IntegerField(blank=True, choices=[(0, 'Không'), (1, 'Có')], default=0, help_text='Noi dung Cham soc - KQ cham soc - cashier_reward', null=True)),
                ('customer_care_transaction', models.IntegerField(blank=True, default=0, help_text='Noi dung Cham soc - KQ cham soc - care_transaction', null=True)),
                ('implement_posm', models.TextField(help_text='Noi dung Trien khai - POSM', null=True)),
                ('implement_merchant_view', models.TextField(help_text='Noi dung Trien khai - merchant_view', null=True)),
                ('implement_career_guideline', models.TextField(help_text='Noi dung Trien khai - career_guideline', null=True)),
                ('implement_confirm', models.IntegerField(blank=True, choices=[(0, 'Cua hang dung dia chi'), (1, 'Cua hang sai dia chi/ da chuyen dia diem'), (2, 'Khong tim duoc cua hang')], help_text='Noi dung xac nhan cua hang', null=True)),
                ('implement_new_address', models.TextField(help_text='Noi dung chuyen den dia chi moi', null=True)),
                ('is_draft', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_report_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_report_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'sale_report_form',
                'ordering': ['-created_date'],
                'default_permissions': (),
            },
        ),
    ]
