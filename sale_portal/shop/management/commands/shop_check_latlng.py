import logging

from django.core.management.base import BaseCommand
from django.db.models import Q

from sale_portal.shop.models import Shop
from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.utils.geo_utils import checkInside


class Command(BaseCommand):
    help = 'Check shop longlat'

    def handle(self, *args, **options):
        cronjob = cron_create(name='shop_check_latlng', type='shop')
        desc = {}
        try:
            self.stdout.write(self.style.SUCCESS('Start command'))
            count = 0
            shops = Shop.objects.filter(Q(activated=1)).exclude(Q(latitude__isnull=True))
            for s in shops:
                if s.wards:
                    s.geo_check = checkInside(s.wards.wards_code, s.latitude, s.longitude)
                else:
                    s.geo_check = -1
                s.save()
                count = count + 1
                if count % 100 == 0:
                    print('Checked: ' + str(count))

            cron_update(cronjob, description=desc)
            self.stdout.write(self.style.SUCCESS('Successfully command'))
        except Exception as e:
            logging.ERROR("Exception shop_check_latlng: {}".format(e))
            desc.update(error_log=str(e))
            cron_update(cronjob, description=desc)
