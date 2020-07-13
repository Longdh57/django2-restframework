# Generated by Django 2.2.7 on 2020-07-13 10:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('sale_promotion_form', '0005_auto_20200211_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='salepromotiontitle',
            name='created_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_promotion_title_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='salepromotiontitle',
            name='reset_data_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='salepromotiontitle',
            name='updated_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sale_promotion_title_updated_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
