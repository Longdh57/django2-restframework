import logging
import pandas as pd
from django.db import connection
from django.core.management.base import BaseCommand

from sale_portal.staff.models import QrStaff
from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.utils.minio_handler import MinioHandler


class Command(BaseCommand):
    help = 'Synchronize data: qr_staff - MINIO to table: qr_staff daily'

    def handle(self, *args, **options):
        cronjob = cron_create(name='qr_staff_sync_daily_minio', type='staff')

        try:

            self.stdout.write(self.style.WARNING('Start qr_staff sync daily processing...'))

            minio_client = MinioHandler().get_instance()
            objects = minio_client.client.list_objects(minio_client.bucket_name, prefix="raw/qr_staff/")
            object_name = None
            for obj in objects:
                if obj._object_name[-3:] == 'csv':
                    object_name = obj._object_name
                    break
            if not object_name:
                raise Exception('Minio qr_staff not exists')

            column_names = ['STAFF_ID', 'NICK_NAME', 'FULL_NAME', 'EMAIL', 'MOBILE', 'DEPARTMENT_CODE', 'STATUS',
                            'CREATED_DATE', 'MODIFY_DATE', 'DEPARTMENT_ID', 'STAFF_CODE']
            converters = {column: str.strip for column in column_names}
            file = minio_client.client.get_object(minio_client.bucket_name, object_name)
            dfs = pd.read_csv(file, converters=converters)

            if len(dfs.columns.tolist()) != len(column_names):
                raise Exception('Format file wrong')

            if len(dfs.values.tolist()) == 0:
                raise Exception('Exception - data qr_staff: COUNT == 0')

            # Truncate table qr_staff before insert all data from Minio
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(QrStaff._meta.db_table))

            print("Step: Truncate table qr_staff before synchronize all data from MMS - MINIO")

            objs = (QrStaff(
                staff_id=int(item[0]),
                nick_name=item[1],
                full_name=item[2],
                email=item[3],
                mobile=item[4],
                department_code=item[5],
                status=item[6],
                created_date=item[7],
                modify_date=item[8],
                department_id=item[9],
                staff_code=item[10],
            ) for item in dfs.values.tolist())

            QrStaff.objects.bulk_create(objs)

            self.stdout.write(self.style.SUCCESS('Finish qr_staff sync daily processing!'))

            cron_update(cronjob, status=1)

        except Exception as e:
            logging.error('Job qr_staff_sync_daily exception: %s', e)
            cron_update(cronjob, status=2, description=str(e))
