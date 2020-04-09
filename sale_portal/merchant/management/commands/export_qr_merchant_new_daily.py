from datetime import datetime
from django.db.models import Q
from django.conf import settings
from django.db import connection
from django.core.management.base import BaseCommand

from sale_portal.merchant.models import QrMerchant
from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.merchant.management.credentials.util_googlespread import *


class Command(BaseCommand):
    help = 'Export qr_merchant new to google spreadsheet daily'

    def get_qr_merchant_count(self):
        qr_merchant_count = QrMerchant.objects.filter(Q(created_date__year=datetime.now().year),
                                                      Q(created_date__month=datetime.now().month)).count()
        return qr_merchant_count

    def get_query(self):
        sql_path = '/sql_query/export_qr_merchant_new_sql.txt'
        f = open(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')) + sql_path, 'r')
        query = f.read()
        f.close()
        return query

    def write(self, spreadObj, content, start_row=2):
        sheet_name = 'QrMerchantNew'

        spread_id = settings.QR_MERCHANT_NEW_SPREAD_ID

        start_col = 'A'

        end_col = 'O'

        start_row = start_row

        return spreadObj.send(spread_id, sheet_name, content, start_col, end_col, start_row)

    def handle(self, *args, **options):
        desc = {}
        cronjob = cron_create(name='export_qr_merchant_new_daily', type='merchant')

        try:
            self.stdout.write(
                self.style.WARNING('Start export Qr_Merchant new to google spreadsheet daily processing...'))

            spreadObj = GoogleSheetWithVerifyCode()

            qr_merchant_count = self.get_qr_merchant_count()

            if qr_merchant_count == 0:
                raise Exception('Exception: Qr_merchant count == 0')

            desc.update(qr_merchant_count=qr_merchant_count)
            cron_update(cronjob, description=desc)

            index = 1

            query = self.get_query()

            with connection.cursor() as cursor:
                cursor.execute(query)
                columns = [col[0] for col in cursor.description]
                data_cursor = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

            content = []

            for item in data_cursor:
                row = [
                    index,
                    item['merchant_code'],
                    item['merchant_brand'],
                    item['merchant_name'],
                    item['created_date'].strftime("%d-%m-%Y"),
                    item['staff_full_name'],
                    item['staff_code'],
                    item['shop_id'],
                    item['shop_province_name'],
                    item['shop_district_name'],
                    item['shop_wards_name'],
                    item['shop_street'],
                    item['shop_address'],
                    item['terminal_id'],
                    item['terminal_name'],
                ]
                content.append(row)
                index = index + 1

            self.write(spreadObj=spreadObj, content=content, start_row=2)

            self.stdout.write(
                self.style.SUCCESS('Finish export Qr_Merchant new to google spreadsheet daily processing!'))

            desc.update(count_index=index)
            cron_update(cronjob, status=1, description=desc)

        except Exception as e:
            desc.update(error_log=str(e))
            cron_update(cronjob, status=2, description=desc)
