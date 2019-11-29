import logging

from django.core.management.base import BaseCommand
from django.db import connection, connections
from itertools import islice

from sale_portal.cronjob.views import cron_create, cron_update
from sale_portal.administrative_unit.models import QrProvince, QrDistrict, QrWards


class Command(BaseCommand):
    help = 'Synchronize table: qr_province, qr_district, qr_wards'

    def truncate_table(self, db_name='qr_province'):
        cursor = connection.cursor()
        cursor.execute('TRUNCATE TABLE ' + db_name + '  RESTART IDENTITY CASCADE')
        return

    def get_query(self, db_name='qr_province', limit=1000, offset=0):
        query = 'select * from ' + db_name + ' order by "ID" limit ' + str(limit) + ' offset ' + str(offset)
        return query

    def get_count(self, db_name='qr_province'):
        cursor = connections['mms'].cursor()
        cursor.execute('select count(*) as total from ' + db_name)
        row = cursor.fetchone()
        print("Count row {}: {}".format(db_name, row[0] if len(row) == 1 else 0))
        return row[0] if len(row) == 1 else 0

    def handle(self, *args, **options):
        cronjob = cron_create(name='administrative_unit_sync', type='system')

        try:
            self.stdout.write(self.style.WARNING('Start qr_province synchronize processing...'))
            limit, offset = 1000, 0
            count_qr_province = self.get_count(db_name='qr_province')
            if count_qr_province > 0:
                self.truncate_table(db_name='qr_province')
                while offset < count_qr_province:
                    query = self.get_query(db_name='qr_province', limit=limit, offset=offset)
                    with connections['mms'].cursor() as cursor:
                        cursor.execute(query)
                        columns = [col[0] for col in cursor.description]
                        data_cursor = [
                            dict(zip(columns, row))
                            for row in cursor.fetchall()
                        ]
                    objs = (QrProvince(
                        id=int(item['ID']),
                        province_code=item['PROVINCE_CODE'],
                        province_name=item['PROVINCE_NAME'],
                        created_date=item['CREATED_DATE'],
                        brand_name=item['BRAND_NAME'],
                    ) for item in data_cursor)
                    batch = list(islice(objs, limit))
                    QrProvince.objects.bulk_create(batch, limit)
                    offset = offset + limit
                self.stdout.write(self.style.SUCCESS('Finish qr_province synchronize processing!'))
            else:
                logging.error('Administrative unit sync: Count qr_province = 0.Force stop qr_province synchronize')
                cron_update(cronjob, description='Count qr_province = 0.Force stop qr_province synchronize')
                self.stdout.write(self.style.ERROR('Count qr_province = 0.Force stop qr_province synchronize!'))

            self.stdout.write(self.style.WARNING('Start qr_district synchronize processing...'))
            limit, offset = 1000, 0
            count_qr_district = self.get_count(db_name='qr_district')
            if count_qr_district > 0:
                self.truncate_table(db_name='qr_district')
                while offset < count_qr_district:
                    query = self.get_query(db_name='qr_district', limit=limit, offset=offset)
                    with connections['mms'].cursor() as cursor:
                        cursor.execute(query)
                        columns = [col[0] for col in cursor.description]
                        data_cursor = [
                            dict(zip(columns, row))
                            for row in cursor.fetchall()
                        ]
                    objs = (QrDistrict(
                        id=int(item['ID']),
                        province_code=item['PROVINCE_CODE'],
                        district_code=item['DISTRICT_CODE'],
                        district_name=item['DISTRICT_NAME'],
                        created_date=item['CREATED_DATE'],
                    ) for item in data_cursor)
                    batch = list(islice(objs, limit))
                    QrDistrict.objects.bulk_create(batch, limit)
                    offset = offset + limit
                self.stdout.write(self.style.SUCCESS('Finish qr_district synchronize processing!'))
            else:
                logging.error('Administrative unit sync: Count qr_district = 0.Force stop qr_district synchronize')
                cron_update(cronjob, description='Count qr_district = 0.Force stop qr_district synchronize')
                self.stdout.write(self.style.ERROR('Count qr_district = 0.Force stop qr_district synchronize!'))

            self.stdout.write(self.style.WARNING('Start qr_wards synchronize processing...'))
            limit, offset = 1000, 0
            count_qr_wards = self.get_count(db_name='qr_wards')
            if count_qr_wards > 0:
                self.truncate_table(db_name='qr_wards')
                while offset < count_qr_wards:
                    query = self.get_query(db_name='qr_wards', limit=limit, offset=offset)
                    with connections['mms'].cursor() as cursor:
                        cursor.execute(query)
                        columns = [col[0] for col in cursor.description]
                        data_cursor = [
                            dict(zip(columns, row))
                            for row in cursor.fetchall()
                        ]
                    objs = (QrWards(
                        id=int(item['ID']),
                        province_code=item['PROVINCE_CODE'],
                        district_code=item['DISTRICT_CODE'],
                        wards_code=item['WARDS_CODE'],
                        wards_name=item['WARDS_NAME'],
                        created_date=item['CREATED_DATE'],
                    ) for item in data_cursor)
                    batch = list(islice(objs, limit))
                    QrWards.objects.bulk_create(batch, limit)
                    print('qr_wards synchronize processing. Row: {}'.format(offset))
                    offset = offset + limit
                self.stdout.write(self.style.ERROR('Finish qr_wards synchronize processing!'))
            else:
                logging.error('Administrative unit sync: Count qr_wards = 0.Force stop qr_wards synchronize')
                cron_update(cronjob, description='Count qr_wards = 0.Force stop qr_wards synchronize')
                self.stdout.write(self.style.ERROR('Count qr_wards = 0.Force stop qr_wards synchronize!'))

            cron_update(cronjob, status=1)

        except Exception as e:
            logging.error('Administrative unit sync: %s', e)
            cron_update(cronjob, status=2, description=str(e))
