import logging
from datetime import date
from itertools import islice

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connections, connection

from sale_portal.shop.models import Shop
from sale_portal.shop_cube.models import ShopCube
from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.utils.refresh_shop_full_data import refresh_shop_full_data


class Command(BaseCommand):
    help = 'Synchronize table: full_shop_cube - DB datawarehouse to table: shop_cube daily'

    def get_query(self, limit=1500, offset=0):
        query = '''
            select *
            from ''' + str(settings.DWH_DB_TABLE) + '''
            where report_date = current_date - 1
            order by shop_id limit ''' + str(limit) + ' offset ' + str(offset)
        return query

    def get_count_shop_cube(self):
        cursor = connections['data_warehouse'].cursor()
        cursor.execute(
            "select count(*) as total from " + str(settings.DWH_DB_TABLE) + " where report_date = current_date - 1")
        row = cursor.fetchone()
        return row[0] if len(row) == 1 else 0

    def handle(self, *args, **options):
        cronjob = cron_create(name='shop_cube_sync_daily', type='shop')

        try:

            self.stdout.write(self.style.WARNING('Start shop_cube sync daily processing...'))

            limit, offset = 1500, 0

            count_shop_cube = self.get_count_shop_cube()

            if count_shop_cube == 0:
                raise Exception("number of shop cube is 0")
            print(f'Count DWH shop_cube row: {count_shop_cube}')

            # Truncate table qr_terminal before synchronize all data from MMS
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}"'.format(ShopCube._meta.db_table))

            print('Truncate table shop_cube before synchronize data from datawarehouse')

            while offset < count_shop_cube:
                query = self.get_query(limit=limit, offset=offset)
                with connections['data_warehouse'].cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    data_cursor = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]

                objs = (ShopCube(
                    shop_id=int(item['shop_id']) if item['shop_id'] != 'Unknown' else 0,
                    merchant_code=item['merchant_code'],
                    merchant_group_bussiness_type=item['merchant_group_bussiness_type'],
                    report_date=item['report_date'],
                    shop_province_name=item['shop_province_name'],
                    shop_district_name=item['shop_district_name'],
                    shop_ward_name=item['shop_ward_name'],
                    department_name=item['department_name'],
                    shop_address=item['shop_address'],
                    number_of_tran=int(item['number_of_tran']),
                    number_of_tran_w_1_7=int(item['number_of_tran_w_1_7']),
                    number_of_tran_w_8_14=int(item['number_of_tran_w_8_14']),
                    number_of_tran_w_15_21=int(item['number_of_tran_w_15_21']),
                    number_of_tran_w_22_end=int(item['number_of_tran_w_22_end']),
                    point_w_1_7=item['point_w_1_7'],
                    point_w_8_14=item['point_w_8_14'],
                    point_w_15_21=item['point_w_15_21'],
                    point_w_22_end=item['point_w_22_end'],
                    point_last_m_w_1_7=item['point_last_m_w_1_7'],
                    point_last_m_w_8_14=item['point_last_m_w_8_14'],
                    point_last_m_w_15_21=item['point_last_m_w_15_21'],
                    point_last_m_w_22_end=item['point_last_m_w_22_end'],
                    voucher_code_list=item['voucher_code_list'],
                    rank=item['rank'],
                    to_do=item['to_do'],
                    _created_date=item['_created_date'],
                    _updated_date=item['_updated_date'],
                ) for item in data_cursor)

                batch = list(islice(objs, limit))

                ShopCube.objects.bulk_create(batch, limit)

                print(f'ShopCube sync daily processing. Row: {offset}/{count_shop_cube}')

                offset = offset + limit

            self.stdout.write(self.style.SUCCESS('Finish shop_cube sync daily processing!'))

            refresh_shop_full_data()

            current_day = date.today().day
            if current_day in [1, 8, 15, 22]:
                print('Start update shop take_care_status at the beginning of each period')
                Shop.objects.all().update(take_care_status=0)
                shop_need_update_id = ShopCube.objects.filter(to_do=1).values('shop_id')
                Shop.objects.filter(pk__in=shop_need_update_id).update(take_care_status=1)
                print('End update shop take_care_status')

            cron_update(cronjob, status=1)

        except Exception as e:
            logging.error('Job shop_cube_sync_daily exception: %s', e)
            cron_update(cronjob, status=2, description=str(e))
