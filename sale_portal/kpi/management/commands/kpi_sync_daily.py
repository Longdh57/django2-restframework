from datetime import datetime
from django.conf import settings
from django.core.management.base import BaseCommand

from sale_portal.kpi.models import Kpi
from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.merchant.management.credentials.util_googlespread import *


class Command(BaseCommand):
    help = 'Synchronize kpi from Gsheet'

    def read(self, spreadObj, sheet_name, range):
        spread_id = settings.KPI_SPREAD_ID
        return spreadObj.read(spreadsheet_id=spread_id, sheet_name=sheet_name, range=range)

    def represents_int(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    def handle(self, *args, **options):
        desc = {}
        cronjob = cron_create(name='kpi_sync_daily', type='kpi')
        self.stdout.write(self.style.WARNING('Start kpi sync daily processing...'))
        try:
            spreadObj = GoogleSheetWithVerifyCode()
            values = self.read(spreadObj=spreadObj, sheet_name='KPI', range='A:F')
            list_email = []
            data = []
            for value in values:
                if self.represents_int(value[1]) and self.represents_int(value[2]) and self.represents_int(value[3]) \
                        and self.represents_int(value[4]) and self.represents_int(value[5]):
                    if int(value[4]) == datetime.now().month and int(value[5]) == datetime.now().year:
                        list_email.append(value[0])
                        data.append({
                            'email': value[0],
                            'kpi_target': int(value[1]),
                            'kpi_point_lcc': int(value[2]),
                            'kpi_point_other': int(value[3]),
                            'month': int(value[4]),
                            'year': int(value[5])
                        })

            desc.update(info_log=str(f'Delete & create kpi row with email in: {list_email}'))
            Kpi.objects.filter(
                email__in=list_email,
                month=datetime.now().month,
                year=datetime.now().year,
            ).delete()

            kpi_objs = [
                Kpi(
                    email=kpi_val['email'],
                    kpi_target=kpi_val['kpi_target'],
                    kpi_point_lcc=kpi_val['kpi_point_lcc'],
                    kpi_point_other=kpi_val['kpi_point_other'],
                    month=kpi_val['month'],
                    year=kpi_val['year']
                )
                for kpi_val in data
            ]
            Kpi.objects.bulk_create(kpi_objs)
            self.stdout.write(self.style.SUCCESS('Finish kpi synchronize processing!'))

            cron_update(cronjob, status=1, description=desc)
        except Exception as e:
            desc.update(error_log=str(e))
            cron_update(cronjob, status=2, description=desc)
