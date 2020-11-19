from django.conf import settings
from django.db import connection
from django.core.management.base import BaseCommand

from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.merchant.management.credentials.util_googlespread import *


class Command(BaseCommand):
    help = 'Export terminal to google spreadsheet daily'

    def get_terminal_query(self):
        sql_path = '/sql_query/export_terminal_sql.txt'
        f = open(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')) + sql_path, 'r')
        query = f.read()
        f.close()
        return query

    def write(self, spreadObj, content, sheet_name='TerminalID', start_col='A', end_col='J', start_row=2):
        sheet_name = sheet_name

        spread_id = settings.TERMINAL_SPREAD_ID

        start_col = start_col

        end_col = end_col

        start_row = start_row

        return spreadObj.send(spread_id, sheet_name, content, start_col, end_col, start_row)

    def export_terminal_id(self):
        self.stdout.write(
            self.style.WARNING('Start export Terminal to google spreadsheet...'))

        spreadObj = GoogleSheetWithVerifyCode()

        index = 1

        query = self.get_terminal_query()

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
                item['terminal_id'],
                item['terminal_name'],
                item['merchant_code'],
                item['merchant_brand'],
                item['merchant_name'],
                item['mer_staff_email'],
                item['code'],
                item['shop_staff_email'],
                item['ter_province_name'],
                item['ter_created_date'].strftime("%d-%m-%Y"),
            ]
            content.append(row)

        self.write(spreadObj=spreadObj, content=content, sheet_name='TerminalID', start_col='A', end_col='J',
                   start_row=2)

        self.stdout.write(
            self.style.SUCCESS('Finish export Terminal to google spreadsheet!'))

    def handle(self, *args, **options):
        desc = {}
        cronjob = cron_create(name='export_terminal_daily', type='terminal')

        try:
            self.export_terminal_id()

            cron_update(cronjob, status=1)

        except Exception as e:
            desc.update(error_log=str(e))
            cron_update(cronjob, status=2, description=desc)
