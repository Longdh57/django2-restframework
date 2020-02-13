# Generated by Django 2.2.7 on 2020-02-13 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0008_stafflog_created_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='role',
            field=models.IntegerField(choices=[(0, 'FREELANCE_STAFF'), (1, 'TEAM_MANAGEMENT'), (2, 'TEAM_STAFF')], default=0),
        ),
        migrations.DeleteModel(
            name='StaffTeamRole',
        ),
    ]
