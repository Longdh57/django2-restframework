# Generated by Django 2.2.7 on 2019-11-13 15:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_auto_20191113_1439'),
        ('terminal', '0002_auto_20191107_1030'),
    ]

    operations = [
        migrations.AddField(
            model_name='terminal',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='terminals', to='shop.Shop'),
        ),
    ]
