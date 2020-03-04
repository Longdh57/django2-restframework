# Generated by Django 2.2.7 on 2019-11-13 09:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        # ('auth', '0011_update_proxy_permissions'),
        ('team', '0001_initial'),
        ('staff', '0002_stafflog'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='team.Team'),
        ),
        migrations.CreateModel(
            name='StaffTeamRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('group', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.Group')),
            ],
            options={
                'db_table': 'staff_team_role',
                'default_permissions': (),
            },
        ),
        migrations.AddField(
            model_name='staff',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='staff.StaffTeamRole'),
        ),
    ]
