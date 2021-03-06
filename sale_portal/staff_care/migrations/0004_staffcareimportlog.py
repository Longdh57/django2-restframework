# Generated by Django 2.2.7 on 2020-02-12 09:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('staff_care', '0003_staffcarelog_is_caring'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffCareImportLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_url', models.FileField(blank=True, help_text='File imported of module staff-care', upload_to='excel/staff-care-import-logs/')),
                ('description', models.TextField(blank=True)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'staff_care_import_log',
                'default_permissions': (),
            },
        ),
    ]
