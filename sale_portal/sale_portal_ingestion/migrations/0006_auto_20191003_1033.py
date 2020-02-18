# Generated by Django 2.1.5 on 2019-10-03 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sale_portal_ingestion', '0005_auto_20190815_1509'),
    ]

    operations = [
        migrations.AddField(
            model_name='midtidshop',
            name='terminal_geo_check',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='midtidshop',
            name='terminal_geo_generate',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='midtidshop',
            name='terminal_latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='midtidshop',
            name='terminal_longitude',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='shoplist',
            name='geo_check',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='shoplist',
            name='geo_generate',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='shoplist',
            name='latitude',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='shoplist',
            name='longitude',
            field=models.FloatField(null=True),
        ),
    ]
