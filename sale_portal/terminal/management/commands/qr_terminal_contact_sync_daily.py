import logging

from itertools import islice
from django.db import connection
from django.db import connections
from django.core.management.base import BaseCommand

from sale_portal.terminal.models import QrTerminalContact
from sale_portal.utils.cronjob_util import cron_create, cron_update


class Command(BaseCommand):
    help = 'Synchronize table: qr_terminal_contact-mms to table: qr_terminal_contact daily'

    def get_query(self, limit=1000, offset=0):
        query = 'select * from qr_terminal_contact order by "ID" limit '+str(limit)+' offset '+str(offset)
        return query

    def get_count_qr_terminal_contact(self):
        cursor = connections['mms'].cursor()
        cursor.execute("select count(*) as total from qr_terminal_contact")
        row = cursor.fetchone()
        return row[0] if len(row) == 1 else 0

    def handle(self, *args, **options):
        cronjob = cron_create(name='qr_terminal_contact_sync_daily', type='terminal')

        try:

            self.stdout.write(self.style.WARNING('Start qr_terminal_contact sync daily processing...'))

            limit, offset = 1500, 0

            count_qr_terminal_contact = self.get_count_qr_terminal_contact()

            # Truncate table qr_terminal_contact before synchronize all data from MMS
            cursor = connection.cursor()
            cursor.execute('TRUNCATE TABLE "{0}" RESTART IDENTITY'.format(QrTerminalContact._meta.db_table))

            print('Truncate table qr_terminal_contact before synchronize all data from MMS')

            while offset < count_qr_terminal_contact:
                query = self.get_query(limit=limit, offset=offset)
                with connections['mms'].cursor() as cursor:
                    cursor.execute(query)
                    columns = [col[0] for col in cursor.description]
                    data_cursor = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]

                objs = (QrTerminalContact(
                    id=int(item['ID']),
                    merchant_code=item['MERCHANT_CODE'],
                    terminal_id=item['TERMINAL_ID'],
                    fullname=item['FULLNAME'],
                    phone=item['PHONE'],
                    phone1=item['PHONE1'],
                    phone2=item['PHONE2'],
                    email=item['EMAIL'],
                    email1=item['EMAIL1'],
                    email2=item['EMAIL2'],
                    created_date=item['CREATED_DATE'],
                    status=item['STATUS'],
                    create_terminal_app=item['CREATE_TERMINAL_APP'],
                    to_create_user=item['TO_CREATE_USER'],
                    to_terminal=item['TO_TERMINAL'],
                    receive_phone=item['RECEIVE_PHONE'],
                    receive_mail=item['RECEIVE_MAIL'],
                ) for item in data_cursor)

                batch = list(islice(objs, limit))

                QrTerminalContact.objects.bulk_create(batch, limit)

                print('QrTerminalContact synchronize processing. Row: ', offset)

                offset = offset+limit

            self.stdout.write(self.style.SUCCESS('Finish qr_terminal_contact sync daily processing!'))

            cron_update(cronjob, status=1)

        except Exception as e:
            logging.error('Job qr_terminal_contact_sync_daily exception: %s', e)
            cron_update(cronjob, status=2, description=str(e))
