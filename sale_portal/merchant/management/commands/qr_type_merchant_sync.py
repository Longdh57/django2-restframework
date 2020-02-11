from django.core.management.base import BaseCommand
from django.db import connections
from itertools import islice
from django.db import connection

from sale_portal.merchant.models import QrTypeMerchant
from sale_portal.utils.cronjob_util import cron_create, cron_update


class Command(BaseCommand):
    help = 'Synchronize table: qr_type_merchant-mms to table: qr_type_merchant daily'

    def get_query(self):
        query = 'select * from qr_type_merchant order by "ID" '
        return query

    def get_count_qr_type_merchant(self):
        cursor = connections['mms'].cursor()
        cursor.execute("select count(*) as total from qr_type_merchant")
        row = cursor.fetchone()
        return row[0] if len(row) == 1 else 0

    def handle(self, *args, **options):
        cronjob = cron_create(name='qr_type_merchant_sync', type='merchant')

        try:

            self.stdout.write(self.style.WARNING('Start qr_type_merchant sync daily processing...'))

            count_qr_type_merchant = self.get_count_qr_type_merchant()
            if count_qr_type_merchant == 0:
                raise Exception('Exception: qr_type_merchant count == 0')

            # Truncate table qr_staff before synchronize all data from MMS
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(QrTypeMerchant._meta.db_table))

            print('Truncate table qr_type_merchant before synchronize all data from MMS')

            query = self.get_query()
            with connections['mms'].cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                data_cursor = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]
            objs = (QrTypeMerchant(
                id=int(item['ID']),
                type_code=item['TYPE_CODE'],
                brand_name=item['BRAND_NAME'],
                full_name=item['FULL_NAME'],
                description=item['DESCRIPTION'],
                created_date=item['CREATED_DATE'],
                updated_date=item['UPDATED_DATE'],
                status=item['STATUS'],
            ) for item in data_cursor)

            batch = list(islice(objs, count_qr_type_merchant))

            QrTypeMerchant.objects.bulk_create(batch, count_qr_type_merchant)

            self.stdout.write(self.style.SUCCESS('Finish qr_type_merchant synchronize processing!'))

            cron_update(cronjob, status=1)

        except Exception as e:
            cron_update(cronjob, status=2, description=str(e))
