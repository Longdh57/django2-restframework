# Generated by Django 2.2.7 on 2019-11-06 17:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('merchant', '0004_auto_20191106_1637'),
    ]

    operations = [
        migrations.CreateModel(
            name='QrTerminal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('terminal_id', models.TextField(null=True)),
                ('merchant_id', models.IntegerField(null=True)),
                ('terminal_name', models.TextField(null=True)),
                ('terminal_address', models.TextField(null=True)),
                ('tax_code', models.TextField(max_length=15, null=True)),
                ('website', models.TextField(null=True)),
                ('website_business', models.TextField(null=True)),
                ('facebook', models.TextField(null=True)),
                ('business_product', models.IntegerField(null=True)),
                ('product_description', models.TextField(null=True)),
                ('register_qr', models.IntegerField(null=True)),
                ('register_vnpayment', models.IntegerField(null=True)),
                ('account_id', models.IntegerField(null=True)),
                ('account_vnmart_id', models.IntegerField(null=True)),
                ('status', models.IntegerField(null=True)),
                ('created_date', models.DateTimeField(null=True)),
                ('modify_date', models.DateTimeField(null=True)),
                ('the_first', models.IntegerField(null=True)),
                ('process_user', models.TextField(null=True)),
                ('denied_approve_desc', models.TextField(null=True)),
                ('process_addition', models.TextField(null=True)),
                ('user_lock', models.TextField(null=True)),
                ('denied_approve_code', models.IntegerField(null=True)),
                ('business_address', models.TextField(null=True)),
                ('register_sms', models.IntegerField(null=True)),
                ('register_ott', models.IntegerField(null=True)),
                ('terminal_app_user', models.TextField(null=True)),
                ('terminal_document', models.TextField(null=True)),
                ('service_code', models.TextField(null=True)),
                ('create_user', models.TextField(null=True)),
                ('visa_pan', models.TextField(null=True)),
                ('master_pan', models.TextField(null=True)),
                ('unionpay_pan', models.TextField(null=True)),
                ('file_name', models.TextField(null=True)),
                ('province_code', models.CharField(max_length=10, null=True)),
                ('district_code', models.CharField(max_length=10, null=True)),
                ('wards_code', models.CharField(max_length=10, null=True)),
            ],
            options={
                'db_table': 'qr_terminal',
                'ordering': ['-created_date'],
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='QrTerminalContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant_code', models.CharField(blank=True, max_length=255, null=True)),
                ('terminal_id', models.CharField(blank=True, max_length=255, null=True)),
                ('fullname', models.CharField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=255, null=True)),
                ('phone1', models.CharField(blank=True, max_length=255, null=True)),
                ('phone2', models.CharField(blank=True, max_length=255, null=True)),
                ('email', models.CharField(blank=True, max_length=255, null=True)),
                ('email1', models.CharField(blank=True, max_length=255, null=True)),
                ('email2', models.CharField(blank=True, max_length=255, null=True)),
                ('created_date', models.DateTimeField(null=True)),
                ('status', models.CharField(blank=True, max_length=255, null=True)),
                ('create_terminal_app', models.DecimalField(blank=True, decimal_places=0, max_digits=38, null=True)),
                ('to_create_user', models.DecimalField(blank=True, decimal_places=0, max_digits=38, null=True)),
                ('to_terminal', models.DecimalField(blank=True, decimal_places=0, max_digits=38, null=True)),
                ('receive_phone', models.CharField(blank=True, max_length=255, null=True)),
                ('receive_mail', models.CharField(blank=True, max_length=255, null=True)),
            ],
            options={
                'db_table': 'qr_terminal_contact',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Terminal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('terminal_id', models.CharField(help_text='Equivalent with qr_terminal.terminal_id', max_length=100, null=True)),
                ('terminal_name', models.CharField(help_text='Equivalent with qr_terminal.terminal_name', max_length=100, null=True)),
                ('terminal_address', models.CharField(help_text='Equivalent with qr_terminal.terminal_address', max_length=255, null=True)),
                ('register_qr', models.IntegerField(help_text='Equivalent with qr_terminal.register_qr', null=True)),
                ('register_vnpayment', models.IntegerField(help_text='Equivalent with qr_terminal.register_vnpayment', null=True)),
                ('status', models.IntegerField(help_text='Equivalent with qr_terminal.status', null=True)),
                ('province_code', models.CharField(help_text='Equivalent with qr_terminal.province_code', max_length=10, null=True)),
                ('district_code', models.CharField(help_text='Equivalent with qr_terminal.district_code', max_length=10, null=True)),
                ('wards_code', models.CharField(help_text='Equivalent with qr_terminal.wards_code', max_length=10, null=True)),
                ('business_address', models.CharField(help_text='Equivalent with qr_terminal.business_address', max_length=255, null=True)),
                ('created_date', models.DateTimeField(help_text='Equivalent with qr_terminal.created_date', null=True)),
                ('modify_date', models.DateTimeField(help_text='Equivalent with qr_terminal.modify_date', null=True)),
                ('merchant', models.ForeignKey(help_text='Equivalent with qr_terminal.merchant_id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='merchant.Merchant')),
            ],
            options={
                'db_table': 'terminal',
                'default_permissions': (),
            },
        ),
    ]
