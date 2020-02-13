# Generated by Django 2.2.7 on 2020-02-13 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_stafflog_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='role',
            field=models.IntegerField(choices=[(0, 'TEAM_STAFF'), (1, 'TEAM_MANAGEMENT'), (99, 'FREELANCE_STAFF')], default=99),
        ),
        migrations.DeleteModel(
            name='StaffTeamRole',
        ),
    ]
