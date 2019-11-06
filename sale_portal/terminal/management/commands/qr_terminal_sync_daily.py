import logging

from itertools import islice
from django.db import connections
from django.db import connection
from django.core.management.base import BaseCommand

from sale_portal.terminal.models import QrTerminal
from sale_portal.cronjob.views import cron_create, cron_update


class Command(BaseCommand):
    help = 'Synchronize table: qr_terminal-mms to table: qr_terminal daily'

    def get_query(self, limit=1000, offset=0):
        query = 'select * from qr_terminal order by "ID" limit ' + str(limit) + ' offset ' + str(offset)
        return query

    def get_count_qr_terminal(self):
        cursor = connections['mms'].cursor()
        cursor.execute("select count(*) as total from qr_terminal")
        row = cursor.fetchone()
        return row[0] if len(row) == 1 else 0

    def handle(self, *args, **options):
        cronjob = cron_create(name='qr_terminal_sync_daily', type='terminal')

        try:

            self.stdout.write(self.style.WARNING('Start qr_terminal sync daily processing...'))

            limit, offset = 1500, 0

            count_qr_terminal = self.get_count_qr_terminal()
            if count_qr_terminal == 0:
                raise Exception('Exception: qr_terminal count == 0')

            # Truncate table qr_terminal before synchronize all data from MMS
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(QrTerminal._meta.db_table))

            print('Truncate table qr_terminal before synchronize all data from MMS')

            while offset < count_qr_terminal:
                query = self.get_query(limit=limit, offset=offset)
                with connections['mms'].cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    data_cursor = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]

                objs = (QrTerminal(
                    id=int(item['ID']),
                    terminal_id=item['TERMINAL_ID'],
                    merchant_id=item['MERCHANT_ID'],
                    terminal_name=item['TERMINAL_NAME'],
                    terminal_address=item['TERMINAL_ADDRESS'],
                    tax_code=item['TAX_CODE'],
                    website=item['WEBSITE'],
                    website_business=item['WEBSITE_BUSINESS'],
                    facebook=item['FACEBOOK'],
                    business_product=item['BUSINESS_PRODUCT'],
                    product_description=item['PRODUCT_DESCRIPTION'],
                    register_qr=item['REGISTER_QR'],
                    register_vnpayment=item['REGISTER_VNPAYMENT'],
                    account_id=item['ACCOUNT_ID'],
                    account_vnmart_id=item['ACCOUNT_VNMART_ID'],
                    status=item['STATUS'],
                    created_date=item['CREATED_DATE'],
                    modify_date=item['MODIFY_DATE'],
                    the_first=item['THE_FIRST'],
                    process_user=item['PROCESS_USER'],
                    denied_approve_desc=item['DENIED_APPROVE_DESC'],
                    process_addition=item['PROCESS_ADDITION'],
                    user_lock=item['USER_LOCK'],
                    denied_approve_code=item['DENIED_APPROVE_CODE'],
                    business_address=item['BUSINESS_ADDRESS'],
                    register_sms=item['REGISTER_SMS'],
                    register_ott=item['REGISTER_OTT'],
                    terminal_app_user=item['TERMINAL_APP_USER'],
                    terminal_document=item['TERMINAL_DOCUMENT'],
                    service_code=item['SERVICE_CODE'],
                    create_user=item['CREATE_USER'],
                    visa_pan=item['VISA_PAN'],
                    master_pan=item['MASTER_PAN'],
                    unionpay_pan=item['UNIONPAY_PAN'],
                    file_name=item['FILE_NAME'],
                    province_code=item['PROVINCE_CODE'],
                    district_code=item['DISTRICT_CODE'],
                    wards_code=item['WARDS_CODE'],
                ) for item in data_cursor)

                batch = list(islice(objs, limit))

                QrTerminal.objects.bulk_create(batch, limit)

                print('QrTerminal sync daily processing. Row: ', offset)

                offset = offset + limit

            self.stdout.write(self.style.SUCCESS('Finish qr_terminal sync daily processing!'))

            cron_update(cronjob, status=1)

        except Exception as e:
            logging.error('Job qr_terminal_sync_daily exception: %s', e)
            cron_update(cronjob, status=2, description=str(e))
