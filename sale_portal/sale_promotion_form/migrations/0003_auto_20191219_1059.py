# Generated by Django 2.2.7 on 2019-12-19 10:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sale_promotion_form', '0002_auto_20191217_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='salepromotion',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_promotion_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='salepromotion',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_promotion_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
