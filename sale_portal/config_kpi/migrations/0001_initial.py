# Generated by Django 2.2.7 on 2020-01-30 14:11

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('area', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangePointPos365',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(0, '6 tháng'), (1, '1 năm'), (2, '2 năm'), (3, 'Trọn đời')], unique=True)),
                ('point', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'exchange_point_pos365',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='ProportionKpiTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.IntegerField(choices=[(0, 'Team có 0 nhân viên vs 1 Team Lead'), (1, 'Team có 1-2 nhân viên vs 1 Team Lead'), (2, 'Team có 3-4 nhân viên vs 1 Team Lead'), (3, 'Team có 5-6 nhân viên vs 1 Team Lead'), (4, 'Team có 7-8 nhân viên vs 1 Team Lead'), (5, 'Team có 9-10 nhân viên vs 1 Team Lead'), (6, 'Team có hơn 10 nhân viên vs 1 Team Lead')])),
                ('leader_coefficient', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='proportion_kpi', to='area.Area')),
            ],
            options={
                'db_table': 'proportion_kpi_team',
                'default_permissions': (),
                'unique_together': {('area', 'type')},
            },
        ),
    ]
