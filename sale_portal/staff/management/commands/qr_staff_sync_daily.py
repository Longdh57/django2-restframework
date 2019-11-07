import logging

from itertools import islice
from django.db import connection, connections
from django.core.management.base import BaseCommand

from sale_portal.staff.models import QrStaff
from sale_portal.cronjob.views import cron_create, cron_update


class Command(BaseCommand):
    help = 'Synchronize table: qr_staff-mms to table: qr_staff daily'

    def get_query(self, limit=1000, offset=0):
        query = 'select * from qr_staff order by "STAFF_ID" limit '+str(limit)+' offset '+str(offset)
        return query

    def get_count_qr_staff(self):
        cursor = connections['mms'].cursor()
        cursor.execute("select count(*) as total from qr_staff")
        row = cursor.fetchone()
        return row[0] if len(row) == 1 else 0

    def handle(self, *args, **options):
        cronjob = cron_create(name='qr_staff_sync_daily', type='staff')

        try:

            self.stdout.write(self.style.WARNING('Start qr_staff sync daily processing...'))

            limit, offset = 100, 0

            count_qr_staff = self.get_count_qr_staff()
            if count_qr_staff == 0:
                raise Exception('Exception: qr_staff count == 0')

            # Truncate table qr_staff before synchronize all data from MMS
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(QrStaff._meta.db_table))

            print('Truncate table qr_staff before synchronize all data from MMS')

            while offset < count_qr_staff:
                query = self.get_query(limit=limit, offset=offset)
                with connections['mms'].cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    data_cursor = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]

                objs = (QrStaff(
                    staff_id=int(item['STAFF_ID']),
                    nick_name = item['NICK_NAME'],
                    full_name = item['FULL_NAME'],
                    email = item['EMAIL'],
                    mobile = item['MOBILE'],
                    department_code = item['DEPARTMENT_CODE'],
                    status = item['STATUS'],
                    created_date = item['CREATED_DATE'],
                    modify_date = item['MODIFY_DATE'],
                    department_id = item['DEPARTMENT_ID'],
                    staff_code=item['STAFF_CODE'],
                ) for item in data_cursor)

                batch = list(islice(objs, limit))

                QrStaff.objects.bulk_create(batch, limit)

                print('QrStaff synchronize processing. Row: ', offset)

                offset = offset+limit

            self.stdout.write(self.style.SUCCESS('Finish qr_staff sync daily processing!'))

            cron_update(cronjob, status=1)

        except Exception as e:
            logging.error('Job qr_staff_sync_daily exception: %s', e)
            cron_update(cronjob, status=2, description=str(e))
