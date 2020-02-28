import os
import logging

from django.db import connection
from django.http import HttpRequest
from django.core.management.base import BaseCommand, CommandError

from sale_portal.user.models import User
from sale_portal.terminal.views import shop_store
from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.terminal.models import Terminal, QrTerminal, TerminalLog


class Command(BaseCommand):
    help = 'Compare table qr_terminal and terminal'

    def get_sql_query(self):
        sql_path = '/sql_query/terminal_synchronize_change_sql.txt'
        f = open(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')) + sql_path, 'r')
        query = f.read()
        f.close()
        return query

    def create_terminal_log(self, terminal=None, qr_terminal=None, status=0):
        old_data, new_data = {}, {}
        try:
            if terminal is not None:
                old_data = {
                    'id': terminal.id,
                    'terminal_id': terminal.terminal_id,
                    'merchant_id': terminal.merchant_id,
                    'terminal_name': terminal.terminal_name,
                    'terminal_address': terminal.terminal_address,
                    'register_qr': terminal.register_qr,
                    'register_vnpayment': terminal.register_vnpayment,
                    'status': terminal.status,
                    'province_code': terminal.province_code,
                    'district_code': terminal.district_code,
                    'wards_code': terminal.wards_code,
                    'business_address': terminal.business_address,
                    'created_date': str(terminal.created_date),
                    'modify_date': str(terminal.modify_date),
                }
            if qr_terminal is not None:
                new_data = {
                    'id': qr_terminal.id,
                    'terminal_id': qr_terminal.terminal_id,
                    'merchant_id': qr_terminal.merchant_id,
                    'terminal_name': qr_terminal.terminal_name,
                    'terminal_address': qr_terminal.terminal_address,
                    'register_qr': qr_terminal.register_qr,
                    'register_vnpayment': qr_terminal.register_vnpayment,
                    'status': qr_terminal.status,
                    'province_code': qr_terminal.province_code,
                    'district_code': qr_terminal.district_code,
                    'wards_code': qr_terminal.wards_code,
                    'business_address': qr_terminal.business_address,
                    'created_date': str(qr_terminal.created_date),
                    'modify_date': str(qr_terminal.modify_date),
                }
            TerminalLog(
                old_data=old_data,
                new_data=new_data,
                type=status,
                terminal_id=qr_terminal.id or None
            ).save()
        except Exception as e:
            logging.error('Job terminal_synchronize_change exception: %s', e)
        return

    def create_new_terminal(self, terminal_id, merchant_id):
        qr_terminal = QrTerminal.objects.filter(terminal_id=terminal_id, merchant_id=merchant_id).first()
        self.create_terminal_log(terminal=None, qr_terminal=qr_terminal, status=0)
        terminal = Terminal(
            id=qr_terminal.id,
            terminal_id=qr_terminal.terminal_id,
            merchant_id=qr_terminal.merchant_id,
            status=qr_terminal.status,
            terminal_address=qr_terminal.terminal_address,
            terminal_name=qr_terminal.terminal_name,
            register_qr=qr_terminal.register_qr,
            register_vnpayment=qr_terminal.register_vnpayment,
            province_code=qr_terminal.province_code,
            district_code=qr_terminal.district_code,
            wards_code=qr_terminal.wards_code,
            business_address=qr_terminal.business_address,
            created_date=qr_terminal.created_date,
            modify_date=qr_terminal.modify_date,
        )
        terminal.save()
        return

    def handle(self, *args, **options):
        cronjob = cron_create(name='terminal_synchronize_change', type='terminal')
        try:
            self.stdout.write(self.style.SUCCESS('Start terminal synchronize change processing...'))
            created, updated = 0, 0
            with connection.cursor() as cursor:
                cursor.execute(self.get_sql_query())
                columns = [col[0] for col in cursor.description]
                data_cursor = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

            for data in data_cursor:
                is_update_business_address = False
                if data['status'] == 0:
                    self.create_new_terminal(terminal_id=data['terminal_id'], merchant_id=data['merchant_id'])
                    created += 1
                    if created % 100 == 0:
                        print('Terminal created: {}'.format(created))
                else:
                    try:
                        qr_terminal = QrTerminal.objects.filter(terminal_id=data['terminal_id'],
                                                                merchant_id=data['merchant_id']).first()
                        terminal = Terminal.objects.filter(terminal_id=data['terminal_id'],
                                                           merchant_id=data['merchant_id']).first()
                        self.create_terminal_log(terminal=terminal, qr_terminal=qr_terminal, status=data['status'])
                        if terminal.business_address != qr_terminal.business_address:
                            is_update_business_address = True

                        terminal.status = qr_terminal.status
                        terminal.terminal_address = qr_terminal.terminal_address
                        terminal.terminal_name = qr_terminal.terminal_name
                        terminal.register_qr = qr_terminal.register_qr
                        terminal.register_vnpayment = qr_terminal.register_vnpayment
                        terminal.province_code = qr_terminal.province_code
                        terminal.district_code = qr_terminal.district_code
                        terminal.wards_code = qr_terminal.wards_code
                        terminal.business_address = qr_terminal.business_address
                        terminal.created_date = qr_terminal.created_date
                        terminal.modify_date = qr_terminal.modify_date
                        terminal.save()

                        if is_update_business_address:
                            if Terminal.objects.filter(shop=terminal.shop).count() == 1:
                                shop = terminal.shop
                                shop.address = qr_terminal.business_address
                                shop.save()
                            else:
                                request = HttpRequest()
                                request.method = 'OTHER'
                                request.user = User.objects.get(pk=1)
                                request.terminal = terminal
                                request.address = terminal.business_address
                                request.street = ''
                                if shop_store(request=request):
                                    self.style.WARNING('Ter update address => Created new shop - ter_id: {}'.format(
                                        terminal.terminal_id))

                        updated += 1
                        if updated % 100 == 0:
                            print(f'Terminal updated: {updated}')

                    except Terminal.DoesNotExist:
                        raise CommandError('Terminal with terminal_id: "%s" | merchant_id: "%s" does not exist' % (
                            data['terminal_id'], data['merchant_id']))

            self.stdout.write(
                self.style.SUCCESS('Successfully command. Created: {}. Updated: {}'.format(created, updated)))

            cron_update(cronjob, status=1)

        except Exception as e:
            logging.error('Job terminal_synchronize_change exception: %s', e)
            cron_update(cronjob, status=2, description=str(e))
