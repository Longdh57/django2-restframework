import logging

from itertools import islice
from django.db import connections, connection
from django.core.management.base import BaseCommand

from sale_portal.shop_cube.models import ShopCube
from sale_portal.cronjob.views import cron_create, cron_update


class Command(BaseCommand):
    help = 'Synchronize table: full_shop_cube - DB datawarehouse to table: shop_cube daily'

    def get_query(self, limit=1000, offset=0):
        query = '''
            select *
            from full_shop_cube
            where report_date = current_date - 1
            order by shop_id limit 
        '''+str(limit)+' offset '+str(offset)
        return query

    def get_count_shop_cube(self):
        cursor = connections['data_warehouse'].cursor()
        cursor.execute("select count(*) as total from full_shop_cube where report_date = current_date - 1")
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

            # Truncate table qr_terminal before synchronize all data from MMS
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}"'.format(ShopCube._meta.db_table))

            print('Truncate table shop_cube before synchronize all data from datawarehouse')

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
                    report_date = item['report_date'],
                    merchant_code = item['merchant_code'],
                    shop_province_code = item['shop_province_code'],
                    shop_province_name = item['shop_province_name'],
                    shop_district_code = item['shop_district_code'],
                    shop_district_name = item['shop_district_name'],
                    shop_ward_code = item['shop_ward_code'],
                    shop_ward_name = item['shop_ward_name'],
                    shop_area = item['shop_area'],
                    shop_address = item['shop_address'],
                    department_name = item['department_name'],
                    sale_name = item['sale_name'],
                    sale_email = item['sale_email'],
                    status = item['status'],
                    merchant_brand = item['merchant_brand'],
                    merchant_group_bussiness_type = item['merchant_group_bussiness_type'],
                    number_of_tran = item['number_of_tran'],
                    value_of_tran = item['value_of_tran'],
                    promotion_value = item['promotion_value'],
                    number_of_new_customer = item['number_of_new_customer'],
                    number_of_customer = item['number_of_customer'],
                    number_of_un_exp_customer = item['number_of_un_exp_customer'],
                    number_of_tran_7d = item['number_of_tran_7d'],
                    value_of_tran_7d = item['value_of_tran_7d'],
                    promotion_value_7d = item['promotion_value_7d'],
                    number_of_new_customer_7d = item['number_of_new_customer_7d'],
                    number_of_customer_7d = item['number_of_customer_7d'],
                    number_of_un_exp_customer_7d = item['number_of_un_exp_customer_7d'],
                    number_of_tran_30d = item['number_of_tran_30d'],
                    value_of_tran_30d = item['value_of_tran_30d'],
                    promotion_value_30d = item['promotion_value_30d'],
                    number_of_new_customer_30d = item['number_of_new_customer_30d'],
                    number_of_customer_30d = item['number_of_customer_30d'],
                    number_of_un_exp_customer_30d = item['number_of_un_exp_customer_30d'],
                    number_of_tran_acm = item['number_of_tran_acm'],
                    value_of_tran_acm = item['value_of_tran_acm'],
                    promotion_value_acm = item['promotion_value_acm'],
                    number_of_new_customer_acm = item['number_of_new_customer_acm'],
                    number_of_customer_acm = item['number_of_customer_acm'],
                    number_of_un_exp_customer_acm = item['number_of_un_exp_customer_acm'],
                    number_of_tran_w_1_7 = item['number_of_tran_w_1_7'],
                    value_of_tran_w_1_7 = item['value_of_tran_w_1_7'],
                    promotion_value_w_1_7 = item['promotion_value_w_1_7'],
                    number_of_new_customer_w_1_7 = item['number_of_new_customer_w_1_7'],
                    number_of_customer_w_1_7 = item['number_of_customer_w_1_7'],
                    number_of_un_exp_customer_w_1_7 = item['number_of_un_exp_customer_w_1_7'],
                    number_of_tran_w_8_14 = item['number_of_tran_w_8_14'],
                    value_of_tran_w_8_14 = item['value_of_tran_w_8_14'],
                    promotion_value_w_8_14 = item['promotion_value_w_8_14'],
                    number_of_new_customer_w_8_14 = item['number_of_new_customer_w_8_14'],
                    number_of_customer_w_8_14 = item['number_of_customer_w_8_14'],
                    number_of_un_exp_customer_w_8_14 = item['number_of_un_exp_customer_w_8_14'],
                    number_of_tran_w_15_21 = item['number_of_tran_w_15_21'],
                    value_of_tran_w_15_21 = item['value_of_tran_w_15_21'],
                    promotion_value_w_15_21 = item['promotion_value_w_15_21'],
                    number_of_new_customer_w_15_21 = item['number_of_new_customer_w_15_21'],
                    number_of_customer_w_15_21 = item['number_of_customer_w_15_21'],
                    number_of_un_exp_customer_w_15_21 = item['number_of_un_exp_customer_w_15_21'],
                    number_of_tran_w_22_end = item['number_of_tran_w_22_end'],
                    value_of_tran_w_22_end = item['value_of_tran_w_22_end'],
                    promotion_value_w_22_end = item['promotion_value_w_22_end'],
                    number_of_new_customer_w_22_end = item['number_of_new_customer_w_22_end'],
                    number_of_customer_w_22_end = item['number_of_customer_w_22_end'],
                    number_of_un_exp_customer_w_22_end = item['number_of_un_exp_customer_w_22_end'],
                    number_of_tran_last_m_w_1_7 = item['number_of_tran_last_m_w_1_7'],
                    value_of_tran_last_m_w_1_7 = item['value_of_tran_last_m_w_1_7'],
                    promotion_value_last_m_w_1_7 = item['promotion_value_last_m_w_1_7'],
                    number_of_new_customer_last_m_w_1_7 = item['number_of_new_customer_last_m_w_1_7'],
                    number_of_customer_last_m_w_1_7 = item['number_of_customer_last_m_w_1_7'],
                    number_of_un_exp_customer_last_m_w_1_7 = item['number_of_un_exp_customer_last_m_w_1_7'],
                    number_of_tran_last_m_w_8_14 = item['number_of_tran_last_m_w_8_14'],
                    value_of_tran_last_m_w_8_14 = item['value_of_tran_last_m_w_8_14'],
                    promotion_value_last_m_w_8_14 = item['promotion_value_last_m_w_8_14'],
                    number_of_new_customer_last_m_w_8_14 = item['number_of_new_customer_last_m_w_8_14'],
                    number_of_customer_last_m_w_8_14 = item['number_of_customer_last_m_w_8_14'],
                    number_of_un_exp_customer_last_m_w_8_14 = item['number_of_un_exp_customer_last_m_w_8_14'],
                    number_of_tran_last_m_w_15_21 = item['number_of_tran_last_m_w_15_21'],
                    value_of_tran_last_m_w_15_21 = item['value_of_tran_last_m_w_15_21'],
                    promotion_value_last_m_w_15_21 = item['promotion_value_last_m_w_15_21'],
                    number_of_new_customer_last_m_w_15_21 = item['number_of_new_customer_last_m_w_15_21'],
                    number_of_customer_last_m_w_15_21 = item['number_of_customer_last_m_w_15_21'],
                    number_of_un_exp_customer_last_m_w_15_21 = item['number_of_un_exp_customer_last_m_w_15_21'],
                    number_of_tran_last_m_w_22_end = item['number_of_tran_last_m_w_22_end'],
                    value_of_tran_last_m_w_22_end = item['value_of_tran_last_m_w_22_end'],
                    promotion_value_last_m_w_22_end = item['promotion_value_last_m_w_22_end'],
                    number_of_new_customer_last_m_w_22_end = item['number_of_new_customer_last_m_w_22_end'],
                    number_of_customer_last_m_w_22_end = item['number_of_customer_last_m_w_22_end'],
                    number_of_un_exp_customer_last_m_w_22_end = item['number_of_un_exp_customer_last_m_w_22_end'],
                    _created_date = item['_created_date'],
                    _updated_date = item['_updated_date'],
                    point_last_m = item['point_last_m'],
                    point_last_m_w_1_7 = item['point_last_m_w_1_7'],
                    point_last_m_w_8_14 = item['point_last_m_w_8_14'],
                    point_last_m_w_15_21 = item['point_last_m_w_15_21'],
                    point_last_m_w_22_end = item['point_last_m_w_22_end'],
                    point_w_1_7 = item['point_w_1_7'],
                    point_w_8_14 = item['point_w_8_14'],
                    point_w_15_21 = item['point_w_15_21'],
                    point_w_22_end = item['point_w_22_end'],
                    bonus_point_this_m = item['bonus_point_this_m'],
                    voucher_code_list = item['voucher_code_list'],
                    current_shop_class = item['current_shop_class'],
                ) for item in data_cursor)

                batch = list(islice(objs, limit))

                ShopCube.objects.bulk_create(batch, limit)

                print('ShopCube sync daily processing. Row: ', offset)

                offset = offset+limit

            self.stdout.write(self.style.SUCCESS('Finish shop_cube sync daily processing!'))

            cron_update(cronjob, status=1)

        except Exception as e:
            logging.error('Job shop_cube_sync_daily exception: %s', e)
            cron_update(cronjob, status=2, description=str(e))
