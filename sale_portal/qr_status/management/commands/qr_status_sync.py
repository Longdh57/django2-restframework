from django.core.management.base import BaseCommand
from django.db import connection, connections
from itertools import islice

from sale_portal.qr_status.models import QrStatus
from sale_portal.cronjob.views import cron_create, cron_update


class Command(BaseCommand):
    help = 'Synchronize table: qr_status'

    def truncate_table(self):
        cursor = connection.cursor()
        cursor.execute('TRUNCATE TABLE qr_status  RESTART IDENTITY')
        return

    def get_query(self):
        query = 'select * from qr_status order by "ID"'
        return query

    def get_count(self):
        cursor = connections['mms'].cursor()
        cursor.execute('select count(*) as total from qr_status')
        row = cursor.fetchone()
        print("Count row qr_status: {}".format(row[0] if len(row) == 1 else 0))
        return row[0] if len(row) == 1 else 0

    def handle(self, *args, **options):
        cronjob = cron_create(name='qr_status_sync', type='system')

        try:
            self.stdout.write(self.style.WARNING('Start qr_status synchronize processing...'))
            count_qr_status = self.get_count()
            if count_qr_status > 0:
                self.truncate_table()
                query = self.get_query()
                with connections['mms'].cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    data_cursor = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
                objs = (QrStatus(
                    id=int(item['ID']),
                    code=item['CODE'],
                    description=item['DESCRIPTION'],
                    type=item['TYPE'],
                    created_date=item['CREATED_DATE'],
                    note=item['NOTE'],
                    icon=item['ICON'],
                ) for item in data_cursor)
                batch = list(islice(objs, 200))
                QrStatus.objects.bulk_create(batch)
                self.stdout.write(self.style.SUCCESS('Finish qr_status synchronize processing!'))
            else:
                cron_update(cronjob, description='Count qr_status = 0.Force stop qr_status synchronize')
                self.stdout.write(self.style.ERROR('Count qr_status = 0.Force stop qr_status synchronize!'))

            cron_update(cronjob, status=1)

        except Exception as e:
            cron_update(cronjob, status=2, description=str(e))
