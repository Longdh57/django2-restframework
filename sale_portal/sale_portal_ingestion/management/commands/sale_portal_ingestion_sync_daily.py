from itertools import islice
from datetime import datetime, time

from django.db.models import Q
from django.conf import settings
from django.db import connections
from django.core.management.base import BaseCommand

from sale_portal.shop.models import Shop
from sale_portal.shop import ShopActivateType
from sale_portal.terminal.models import Terminal
from sale_portal.cronjob.models import CronjobLog
from sale_portal.sale_portal_ingestion import send_log_email
from sale_portal.sale_portal_ingestion.models import ShopList, MidTidShop


class Command(BaseCommand):
    help = 'Synchronize table: shop, merchant, terminal - SalePortal ' \
           'to ' \
           'table: shop_list, mid_tid_shop - SalePortalIngestion'

    def retry(self, name, type):
        today = datetime.now().date()
        today_start = datetime.combine(today, time())
        job_log = CronjobLog.objects.filter(name=name, type=type, created_date__gte=today_start)

        if job_log.filter(status=1).count() > 0:
            return True
        else:
            count_time_error = job_log.filter(~Q(status=1)).count()
            return count_time_error

    def shop_list_action(self, db_name='sale_portal_ingestion'):
        self.stdout.write('Table shop_list processing...')

        limit, offset = 1000, 0

        shop_without_register_vnpayments = Terminal.objects.filter(
            Q(shop_id__isnull=False),
            ~Q(register_vnpayment=1)).values('shop_id').distinct()

        count_shop = Shop.objects.order_by('id').filter(activated=ShopActivateType.ACTIVATE,
                                                        id__in=shop_without_register_vnpayments).count()

        # Truncate table shop_list before synchronize all data from MMS
        print('Truncate shop_list before processing')
        with connections[db_name].cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(ShopList._meta.db_table))

        while offset < count_shop:
            shops = Shop.objects.order_by('id').filter(
                activated=ShopActivateType.ACTIVATE,
                id__in=shop_without_register_vnpayments)[offset:(offset + limit)]

            print('START')

            objs = (ShopList(
                shop_id=item.code,
                shop_province_code=item.province.province_code if item.province is not None else None,
                shop_province_name=item.province.province_name if item.province is not None else None,
                shop_district_code=item.district.district_code if item.district is not None else None,
                shop_district_name=item.district.district_name if item.district is not None else None,
                shop_ward_code=item.wards.wards_code if item.wards is not None else None,
                shop_ward_name=item.wards.wards_name if item.wards is not None else None,
                shop_area=item.street,
                shop_address=item.address,
                merchant_code=item.merchant.merchant_code if item.merchant is not None else None,
                merchant_brand=item.merchant.merchant_brand if item.merchant is not None else None,
                department_name=item.team.code if item.team is not None else None,
                sale_name=item.staff.full_name if item.staff is not None else None,
                sale_email=item.staff.email if item.staff is not None else None,
                merchant_group_bussiness_type=item.merchant.get_type().type_code if item.merchant.get_type() is not None else None,
                status='Chăm sóc' if item.take_care_status == 1 else 'Không chăm sóc',
                shop_created_date=item.created_date,
                longitude=item.longitude,
                latitude=item.latitude
            ) for item in shops)

            batch = list(islice(objs, limit))

            ShopList.objects.using(db_name).bulk_create(batch, limit)

            print('ShopList synchronize processing. Row: ', offset)

            offset = offset + limit

        self.stdout.write(self.style.SUCCESS('Finish table shop_list processing!'))

        return count_shop

    def mid_tid_shop_action(self, db_name='sale_portal_ingestion'):

        self.stdout.write('Table mid_tid_shop processing...')

        limit, offset = 1000, 0

        count_terminal = Terminal.objects.filter(Q(shop_id__isnull=False), ~Q(register_vnpayment=1)).count()

        # Truncate table mid_tid_shop before synchronize all data from MMS
        print('Truncate mid_tid_shop before processing')
        with connections[db_name].cursor() as cursor:
            cursor.execute('TRUNCATE TABLE "{0}" CASCADE'.format(MidTidShop._meta.db_table))

        while offset < count_terminal:
            terminals = Terminal.objects.order_by('id').filter(
                Q(shop_id__isnull=False),
                ~Q(register_vnpayment=1))[offset:(offset + limit)]

            objs = (MidTidShop(
                terminal_id=item.terminal_id,
                terminal_name=item.terminal_name,
                merchant_code=item.merchant.merchant_code if item.merchant is not None else None,
                merchant_name=item.merchant.merchant_name if item.merchant is not None else None,
                shop_id=item.shop.code if item.shop is not None else None,
            ) for item in terminals)

            batch = list(islice(objs, limit))

            MidTidShop.objects.using(db_name).bulk_create(batch, limit)

            print('MidTidShop synchronize processing. Row: ', offset)

            offset = offset + limit

        self.stdout.write(self.style.SUCCESS('Finish table mid_tid_shop processing!'))

        return count_terminal

    def add_arguments(self, parser):
        parser.add_argument('--run_by_os', type=int,
                            help='If process running by OS system, add run_by_os 1 to command')
        parser.add_argument('--database', type=str,
                            help='Default process running for db sale_portal_ingestion, add db name to change '
                                 'to sale_portal_ingestion_new')

    def handle(self, *args, **options):
        name = 'sale_portal_ingestion_sync_daily'
        type = 'shop'
        desc = {}

        retry = self.retry(name=name, type=type)

        run_by_os = 0
        database = 'sale_portal_ingestion'
        if options['run_by_os'] is not None:
            run_by_os = options['run_by_os']

        if options['database'] is not None:
            database = options['database']

        print("DB name: {}".format(database))

        if run_by_os == 0:
            print('Job is running manual by admin, always run without check retry')
            pass
        else:
            print('Retry: {}'.format(retry))
            if retry is True:
                print('Job was running and success before this time')
                return
            else:
                if retry >= 3:
                    # send email
                    print('Job was error and retry more than 3 times, system will send Email to admin')
                    send_log_email(
                        job_name=name,
                        message_error='Job was error and retry more than 3 times',
                        admin_emails=settings.LIST_ADMINISTRATOR_EMAIL
                    )
                    return

        cron_log = CronjobLog(
            name=name,
            type=type
        )
        cron_log.save()

        try:
            self.stdout.write(self.style.WARNING('Start sale_portal_ingestion synchronize daily processing...'))

            # count_shop = self.shop_list_action(db_name=database)
            # desc.update(count_shop=count_shop)
            # cron_log.description = desc
            # cron_log.save()

            count_terminal = self.mid_tid_shop_action(db_name=database)
            desc.update(count_terminal=count_terminal)
            cron_log.description = desc
            cron_log.save()

            self.stdout.write(self.style.SUCCESS('Finish sale_portal_ingestion synchronize daily processing!'))

            cron_log.status = 1
            cron_log.save()

        except Exception as e:
            cron_log.status = 2
            cron_log.description = str(e)
            cron_log.save()
