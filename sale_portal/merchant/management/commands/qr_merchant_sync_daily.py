from django.core.management.base import BaseCommand
from django.db import connections
from itertools import islice
from django.db import connection

from sale_portal.merchant.models import QrMerchant
from sale_portal.cronjob.views import cron_create, cron_update


class Command(BaseCommand):
    help = 'Synchronize table: qr_merchant-mms to table: qr_merchant daily'

    def get_query(self, limit=1000, offset=0):
        query = 'select * from qr_merchant order by "ID" limit '+str(limit)+' offset '+str(offset)
        return query

    def get_count_qr_merchant(self):
        cursor = connections['mms'].cursor()
        cursor.execute("select count(*) as total from qr_merchant")
        row = cursor.fetchone()
        return row[0] if len(row) == 1 else 0

    def handle(self, *args, **options):
        cronjob = cron_create(name='qr_merchant_sync_daily', type='merchant')

        try:

            self.stdout.write(self.style.WARNING('Start qr_merchant sync daily processing...'))

            limit, offset = 1000, 0

            count_qr_merchant = self.get_count_qr_merchant()
            if count_qr_merchant == 0:
                raise Exception('Exception: qr_merchant count == 0')

            # Truncate table qr_staff before synchronize all data from MMS
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(QrMerchant._meta.db_table))

            print('Truncate table qr_merchant before synchronize all data from MMS')

            while offset < count_qr_merchant:
                query = self.get_query(limit=limit, offset=offset)
                with connections['mms'].cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    data_cursor = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
                objs = (QrMerchant(
                    id=int(item['ID']),
                    merchant_code=item['MERCHANT_CODE'],
                    service_code=item['SERVICE_CODE'],
                    merchant_brand=item['MERCHANT_BRAND'],
                    merchant_name=item['MERCHANT_NAME'],
                    merchant_type=item['MERCHANT_TYPE'],
                    address=item['ADDRESS'],
                    description=item['DESCRIPTION'],
                    status=item['STATUS'],
                    website=item['WEBSITE'],
                    master_merchant_code=item['MASTER_MERCHANT_CODE'],
                    province_code=item['PROVINCE_CODE'],
                    district_code=item['DISTRICT_CODE'],
                    department =item['DEPARTMENT_ID'],
                    staff =item['STAFF_ID'],
                    genqr_checksum =item['GENQR_CHECKSUM'],
                    genqr_accesskey =item['GENQR_ACCESSKEY'],
                    switch_code =item['SWITCH_CODE'],
                    created_date =item['CREATED_DATE'],
                    modify_date =item['MODIFY_DATE'],
                    process_user =item['PROCESS_USER'],
                    denied_approve_desc =item['DENIED_APPROVE_DESC'],
                    create_user =item['CREATE_USER'],
                    org_status =item['ORG_STATUS'],
                    email_vnpay =item['EMAIL_VNPAY'],
                    pass_email_vnpay =item['PASS_EMAIL_VNPAY'],
                    process_addition =item['PROCESS_ADDITION'],
                    denied_approve_code =item['DENIED_APPROVE_CODE'],
                    business_address =item['BUSINESS_ADDRESS'],
                    app_user =item['APP_USER'],
                    pin_code =item['PIN_CODE'],
                    provider_code =item['PROVIDER_CODE'],
                    wards_code =item['WARDS_CODE'],
                ) for item in data_cursor)

                batch = list(islice(objs, limit))

                QrMerchant.objects.bulk_create(batch, limit)

                print('QrMerchant synchronize processing. Row: ', offset)

                offset = offset+limit

            self.stdout.write(self.style.SUCCESS('Finish qr_merchant synchronize processing!'))

            cron_update(cronjob, status=1)

        except Exception as e:
            cron_update(cronjob, status=2, description=str(e))
