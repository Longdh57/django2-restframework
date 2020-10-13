import datetime as dt
from django.conf import settings
from django.db import connection
from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from sale_portal.shop.models import Shop
from sale_portal.merchant.models import Merchant
from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.merchant.management.credentials.util_googlespread import *


class Command(BaseCommand):
    help = 'Export merchant new and shop new in this month to google spreadsheet daily'

    def get_day_22_last_month(self):
        today = dt.date.today()
        lastMonth = today + relativedelta(months=-1)
        return lastMonth.replace(day=22)

    def get_merchant_count(self):
        merchant_count = Merchant.objects.filter(created_date__gte=self.get_day_22_last_month()).count()
        return merchant_count

    def get_shop_count(self):
        shop_count = Shop.objects.filter(created_date__gte=self.get_day_22_last_month()).count()
        return shop_count

    def get_merchant_new_query(self):
        sql_path = '/sql_query/export_merchant_new_sql.txt'
        f = open(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')) + sql_path, 'r')
        query = f.read()
        f.close()
        return query

    def get_shop_new_query(self):
        sql_path = '/sql_query/export_shop_new_sql.txt'
        f = open(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')) + sql_path, 'r')
        query = f.read()
        f.close()
        return query

    def write(self, spreadObj, content, sheet_name='QrMerchantNew', start_col='A', end_col='O', start_row=2):
        sheet_name = sheet_name

        spread_id = settings.QR_MERCHANT_NEW_SPREAD_ID

        start_col = start_col

        end_col = end_col

        start_row = start_row

        return spreadObj.send(spread_id, sheet_name, content, start_col, end_col, start_row)

    def export_merchant_new(self):
        self.stdout.write(
            self.style.WARNING('Start export Qr_Merchant new to google spreadsheet daily processing...'))

        spreadObj = GoogleSheetWithVerifyCode()

        merchant_count = self.get_merchant_count()

        if merchant_count == 0:
            raise Exception('Exception: Merchant count == 0')

        index = 1

        query = self.get_merchant_new_query()

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
                item['staff_email'],
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

        self.write(spreadObj=spreadObj, content=content, sheet_name='QrMerchantNew', start_col='A', end_col='P',
                   start_row=2)

        self.stdout.write(
            self.style.SUCCESS('Finish export Merchant new to google spreadsheet daily processing!'))

    def export_shop_new(self):
        self.stdout.write(
            self.style.WARNING('Start export Shop new to google spreadsheet daily processing...'))

        spreadObj = GoogleSheetWithVerifyCode()

        shop_count = self.get_shop_count()

        if shop_count == 0:
            raise Exception('Exception: Shop count == 0')

        index = 1

        query = self.get_shop_new_query()

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
                item['merchant_staff_email'],
                item['merchant_created_date'].strftime("%d-%m-%Y"),
                item['staff_full_name'],
                item['staff_code'],
                item['staff_email'],
                item['shop_id'],
                item['shop_province_name'],
                item['shop_district_name'],
                item['shop_wards_name'],
                item['shop_street'],
                item['shop_address'],
                item['shop_created_date'].strftime("%d-%m-%Y"),
                item['terminal_id'],
                item['terminal_name'],
                item['merchant_type_name']
            ]
            content.append(row)
            index = index + 1

        self.write(spreadObj=spreadObj, content=content, sheet_name='ShopNew', start_col='A', end_col='S', start_row=2)

        self.stdout.write(
            self.style.SUCCESS('Finish export Shop new to google spreadsheet daily processing!'))

    def handle(self, *args, **options):
        desc = {}
        cronjob = cron_create(name='export_qr_merchant_new_daily', type='merchant')

        try:
            self.export_merchant_new()

            self.export_shop_new()

            cron_update(cronjob, status=1)

        except Exception as e:
            desc.update(error_log=str(e))
            cron_update(cronjob, status=2, description=desc)
