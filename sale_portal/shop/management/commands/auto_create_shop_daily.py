import logging
from django.db.models import Q
from django.http import HttpRequest
from django.core.management.base import BaseCommand

from sale_portal.user.models import User
from sale_portal.shop.models import Shop
from sale_portal.shop import ShopActivateType
from sale_portal.terminal.models import Terminal
from sale_portal.terminal.views import shop_store
from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.utils.refresh_shop_full_data import refresh_shop_full_data


class Command(BaseCommand):
    help = 'Auto create new shop from terminal daily'

    def handle(self, *args, **options):
        cronjob = cron_create(name='auto_create_shop_daily', type='shop')
        desc = {}

        total_row = 0

        try:
            self.stdout.write(self.style.WARNING('Start Auto create new shop from terminal daily processing...'))

            # suggestion_lists la danh sach cac ter có thể trùng
            suggestion_lists = []
            suggestion_query = Terminal.objects.raw('''
                            select t.id
                            from terminal t
                                   inner join shop s on t.merchant_id = s.merchant_id and t.wards_code = (select wards_code
                                                                                                          from qr_wards
                                                                                                          where s.wards_id = qr_wards.id)
                            where t.shop_id is null
                              and t.register_vnpayment <> 1
                              and s.activated = 1
                            group by t.id
                        ''')
            for item in suggestion_query:
                suggestion_lists.append(item.id)
            terminals = Terminal.objects.filter(Q(shop=None) & ~Q(status=-1))

            # terminal_for_creates la danh sach terminal co the su dung de tao shop
            terminal_for_creates = terminals.filter(~Q(id__in=suggestion_lists), ~Q(register_vnpayment=1))

            if terminals.count() == 0:
                raise Exception('Exception: Count Terminal none shop and status = -1 is 0')
            else:
                desc.update(terminal_count=terminals.count())
                desc.update(terminal_warnings=terminals.filter(id__in=suggestion_lists).count())
                desc.update(terminal_for_creates=terminal_for_creates.count())
                cron_update(cronjob, description=desc)

            for terminal in terminal_for_creates:
                if Shop.objects.filter(
                        merchant_id=terminal.merchant_id,
                        activated=ShopActivateType.ACTIVATE,
                        wards__wards_code=terminal.wards_code
                ).first():
                    desc.update(terminal_warnings=desc['terminal_warnings'] + 1)
                else:
                    request = HttpRequest()
                    request.method = 'OTHER'
                    request.user = User.objects.get(pk=1)
                    request.terminal = terminal
                    request.address = terminal.business_address
                    request.street = ''

                    if shop_store(request=request):
                        total_row += 1

                    if total_row % 100 == 0:
                        print('Created total: ' + str(total_row) + 'shops')

            self.stdout.write(self.style.SUCCESS('Finish Auto create new shop from terminal daily processing!'))

            refresh_shop_full_data()

            desc.update(total_shop_created=total_row)
            cron_update(cronjob, description=desc, status=1)

        except Exception as e:
            logging.ERROR("Exception auto_create_shop_daily: {}".format(e))
            desc.update(error_log=str(e))
            cron_update(cronjob, description=desc, status=2)
