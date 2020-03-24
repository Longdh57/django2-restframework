import logging

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from sale_portal.shop.models import Shop
from sale_portal.utils.cronjob_util import cron_create, cron_update
from sale_portal.utils.geo_utils import checkInside


class Command(BaseCommand):
    help = 'Get shop longlat by google api and check longlat'

    def handle(self, *args, **options):
        cronjob = cron_create(name='shop_update_latlng_daily', type='shop')
        desc = {}
        count_success = 0
        count_failed = 0
        list_failed = []
        try:
            self.stdout.write(self.style.SUCCESS('Start shop geodata daily processing...'))
            exception_desctiption = []
            limit = settings.LIMIT_QUERY_PER_GOOGLE_ACCOUNT_TOKEN
            list_token = settings.LIST_GEODATA_GOOGLE_ACCOUNT_TOKEN

            for token in list_token:
                shops = Shop.objects.filter(
                    Q(activated=1) & Q(latitude__isnull=True)
                ).exclude(
                    Q(address='') | Q(address='0') | Q(geo_generate=-1)
                )[:limit]

                if shops is None or len(shops) == 0:
                    raise Exception('Do not have any shop that need to query')
                geodecode_url = 'https://maps.googleapis.com/maps/api/geocode/json'
                for s in shops:
                    params = {'key': token, 'address': s.address}
                    try:
                        r = requests.get(geodecode_url, params=params)
                        results = r.json()['results']
                        location = results[0]['geometry']['location']
                        s.latitude = location['lat']
                        s.longitude = location['lng']
                        s.geo_check = checkInside(s.wards.wards_code, s.latitude, s.longitude)
                        s.geo_generate = 1
                        s.save()
                        count_success = count_success + 1
                        desc.update(count_success=count_success)
                        print('Update success shop: ' + str(s.id))
                    except Exception as inst:
                        s.geo_generate = -1
                        s.save()
                        count_failed = count_failed + 1
                        list_failed.append(s.id)
                        desc.update(count_failed=count_failed)
                        desc.update(list_failed=list_failed)
                        print('Update ' + str(s.id) + ' failed: ' + str(inst))
            cron_update(cronjob, description=desc)
            self.stdout.write(self.style.SUCCESS('Successfully command'))

        except Exception as e:
            desc.update(error_log=str(e))
            cron_update(cronjob, description=desc)
