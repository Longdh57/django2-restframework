from django.core.management.base import BaseCommand
from django.db import connections
from itertools import islice
from django.db import connection

from sale_portal.merchant.models import QrMerchantInfo
from sale_portal.utils.cronjob_util import cron_create, cron_update


class Command(BaseCommand):
    help = 'Synchronize table: qr_merchant_info-mms to table: qr_merchant_info daily'

    def get_query(self, limit=1000, offset=0):
        query = 'select * from qr_merchant_info order by "ID" limit ' + str(limit) + ' offset ' + str(offset)
        return query

    def get_count_qr_merchant_info(self):
        cursor = connections['mms'].cursor()
        cursor.execute("select count(*) as total from qr_merchant_info")
        row = cursor.fetchone()
        return row[0] if len(row) == 1 else 0

    def handle(self, *args, **options):
        cronjob = cron_create(name='qr_merchant_info_sync', type='merchant')

        try:

            self.stdout.write(self.style.WARNING('Start qr_merchant_info sync daily processing...'))

            limit, offset = 1000, 0

            count_qr_merchant_info = self.get_count_qr_merchant_info()
            if count_qr_merchant_info == 0:
                raise Exception('Exception: qr_merchant_info count == 0')

            # Truncate table qr_staff before synchronize all data from MMS
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(QrMerchantInfo._meta.db_table))

            print('Truncate table qr_merchant_info before synchronize all data from MMS')

            while offset < count_qr_merchant_info:
                query = self.get_query(limit=limit, offset=offset)
                with connections['mms'].cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    data_cursor = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
                objs = (QrMerchantInfo(
                    id=int(item['ID']),
                    merchant_code=item['MERCHANT_CODE'],
                    rm_auth=item['RM_AUTH'],
                    register_sms=item['REGISTER_SMS'],
                    register_ott=item['REGISTER_OTT'],
                    to_create_user=item['TO_CREATE_USER'],
                    to_merchant=item['TO_MERCHANT'],
                    receive_phone=item['RECEIVE_PHONE'],
                    receive_email=item['RECEIVE_EMAIL'],
                    contact_name=item['CONTACT_NAME'],
                    contact_phone=item['CONTACT_PHONE'],
                    contact_email=item['CONTACT_EMAIL'],
                    contact_phone1=item['CONTACT_PHONE1'],
                    contact_phone2=item['CONTACT_PHONE2'],
                    contact_email1=item['CONTACT_EMAIL1'],
                    contact_email2=item['CONTACT_EMAIL2'],
                ) for item in data_cursor)

                batch = list(islice(objs, limit))

                QrMerchantInfo.objects.bulk_create(batch, limit)

                print('QrMerchantInfo synchronize processing. Row: ', offset)

                offset = offset + limit

            self.stdout.write(self.style.SUCCESS('Finish qr_merchant_info synchronize processing!'))

            cron_update(cronjob, status=1)

        except Exception as e:
            cron_update(cronjob, status=2, description=str(e))
