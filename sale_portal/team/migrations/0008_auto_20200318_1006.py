# Generated by Django 2.2.7 on 2020-03-18 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0007_team_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='target_kpi_pos365',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='team',
            name='target_kpi_s73',
            field=models.IntegerField(null=True),
        ),
    ]
