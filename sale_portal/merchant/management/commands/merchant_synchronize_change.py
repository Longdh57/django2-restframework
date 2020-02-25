import os
import logging

from django.db import connection
from django.core.management.base import BaseCommand, CommandError

from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.merchant.models import Merchant, QrMerchant, MerchantLog


class Command(BaseCommand):
    help = 'Compare table qr_merchant and merchant'

    def get_sql_query(self):
        sql_path = '/sql_query/merchant_synchronize_change_sql.txt'
        f = open(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')) + sql_path, 'r')
        query = f.read()
        f.close()
        return query

    def create_merchant_log(self, merchant=None, qr_merchant=None, status=0):
        old_data, new_data = {}, {}
        try:
            if merchant is not None:
                old_data = {
                    'id': merchant.id,
                    'merchant_code': merchant.merchant_code,
                    'merchant_name': merchant.merchant_name,
                    'merchant_brand': merchant.merchant_brand,
                    'merchant_type': merchant.merchant_type,
                    'address': merchant.address,
                    'description': merchant.description,
                    'status': merchant.status,
                    'department': merchant.department,
                    'province_code': qr_merchant.province_code,
                    'district_code': qr_merchant.district_code,
                    'wards_code': qr_merchant.wards_code,
                    'staff': merchant.staff,
                    'created_date': str(merchant.created_date),
                    'modify_date': str(merchant.modify_date),
                }
            if qr_merchant is not None:
                new_data = {
                    'id': qr_merchant.id,
                    'merchant_code': qr_merchant.merchant_code,
                    'merchant_name': qr_merchant.merchant_name,
                    'merchant_brand': qr_merchant.merchant_brand,
                    'merchant_type': qr_merchant.merchant_type,
                    'address': qr_merchant.address,
                    'description': qr_merchant.description,
                    'status': qr_merchant.status,
                    'department': qr_merchant.department,
                    'province_code': qr_merchant.province_code,
                    'district_code': qr_merchant.district_code,
                    'wards_code': qr_merchant.wards_code,
                    'staff': qr_merchant.staff,
                    'created_date': str(qr_merchant.created_date),
                    'modify_date': str(qr_merchant.modify_date),
                }
            MerchantLog(
                old_data=old_data,
                new_data=new_data,
                type=status,
                merchant_id=qr_merchant.id or None
            ).save()
        except Exception as e:
            logging.error('Job merchant_synchronize_change exception: %s', e)
        return

    def create_new_merchant(self, merchant_id):
        qr_merchant = QrMerchant.objects.filter(id=merchant_id).first()
        self.create_merchant_log(merchant=None, qr_merchant=qr_merchant, status=0)
        merchant = Merchant(
            id=qr_merchant.id,
            merchant_code=qr_merchant.merchant_code,
            merchant_name=qr_merchant.merchant_name,
            merchant_brand=qr_merchant.merchant_brand,
            merchant_type=qr_merchant.merchant_type,
            address=qr_merchant.address,
            description=qr_merchant.description,
            status=qr_merchant.status,
            department=qr_merchant.department,
            province_code=qr_merchant.province_code,
            district_code=qr_merchant.district_code,
            wards_code=qr_merchant.wards_code,
            staff=qr_merchant.staff,
            created_date=qr_merchant.created_date,
            modify_date=qr_merchant.modify_date,
        )
        merchant.save()
        return

    def handle(self, *args, **options):
        cronjob = cron_create(name='merchant_synchronize_change', type='merchant')
        try:
            self.stdout.write(self.style.SUCCESS('Start merchant synchronize change processing...'))
            created, updated = 0, 0
            with connection.cursor() as cursor:
                cursor.execute(self.get_sql_query())
                columns = [col[0] for col in cursor.description]
                data_cursor = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

            for data in data_cursor:
                if data['status'] == 0:
                    self.create_new_merchant(merchant_id=data['merchant_id'])
                    created += 1
                    if created % 100 == 0:
                        print('Merchant created: {}'.format(created))
                else:
                    try:
                        qr_merchant = QrMerchant.objects.filter(id=data['merchant_id']).first()
                        merchant = Merchant.objects.get(pk=data['merchant_id'])

                        self.create_merchant_log(merchant=merchant, qr_merchant=qr_merchant, status=data['status'])

                        merchant.merchant_code = qr_merchant.merchant_code
                        merchant.merchant_name = qr_merchant.merchant_name
                        merchant.merchant_brand = qr_merchant.merchant_brand
                        merchant.merchant_type = qr_merchant.merchant_type
                        merchant.address = qr_merchant.address
                        merchant.description = qr_merchant.description
                        merchant.status = qr_merchant.status
                        merchant.department = qr_merchant.department
                        merchant.province_code = qr_merchant.province_code
                        merchant.district_code = qr_merchant.district_code
                        merchant.wards_code = qr_merchant.wards_code
                        merchant.staff = qr_merchant.staff
                        merchant.created_date = qr_merchant.created_date
                        merchant.modify_date = qr_merchant.modify_date
                        merchant.save()

                        updated += 1
                        if updated % 100 == 0:
                            print('Merchant updated: {}'.format(updated))

                    except Merchant.DoesNotExist:
                        raise CommandError('Merchant with merchant_id: "%s" does not exist' % (
                            data['merchant_id']))

            self.stdout.write(
                self.style.SUCCESS('Successfully command. Created: {}. Updated: {}'.format(created, updated)))

            cron_update(cronjob, status=1)

        except Exception as e:
            logging.error('Job merchant_synchronize_change exception: %s', e)
            cron_update(cronjob, status=2, description=str(e))
