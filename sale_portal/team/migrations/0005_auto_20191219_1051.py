# Generated by Django 2.2.7 on 2019-12-19 10:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('team', '0004_auto_20191218_1525'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='team',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='teamlog',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='team_log_created_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
