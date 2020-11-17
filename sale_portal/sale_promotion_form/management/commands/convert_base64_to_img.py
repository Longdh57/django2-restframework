import os
import base64
import logging
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand

from sale_portal.sale_promotion_form.models import SalePromotion


class Command(BaseCommand):
    help = 'Convert DB base64 to image and return img-url'

    def add_arguments(self, parser):
        parser.add_argument('--time', type=str, help='Time to get promotion form')

    def handle(self, *args, **options):
        time = datetime.now()
        if options['time'] is not None:
            time = datetime.strptime(options['time'], '%d-%m-%Y')

        promotion_forms = SalePromotion.objects.filter(
            updated_date__gte=time.replace(hour=0, minute=0, second=0),
            updated_date__lt=time.replace(hour=23, minute=59, second=59),
            image__isnull=False,
            sub_image__isnull=False
        ).all()
        if len(promotion_forms) > 0:
            location = settings.FS_IMAGE_UPLOADS + time.date().isoformat()
            base_url = settings.FS_IMAGE_URL + time.date().isoformat()
            if not os.path.exists(location):
                os.makedirs(location)

            for prf in promotion_forms:
                if prf.image[0:23] != 'data:image/jpeg;base64,':
                    continue
                print(f'[x] Promotion form id: <{prf.id}>')
                promo_img_filename = str(prf.updated_by_id) + '-promo_image' + str(prf.updated_date.timestamp()) + '.png'
                with open(location + '/' + promo_img_filename, "wb") as f:
                    f.write(base64.b64decode(prf.image[23:]))
                    f.close()
                    prf.image = base_url + '/' + promo_img_filename
                promo_sub_img_filename = str(prf.updated_by_id) + '-promo_sub_image' + str(
                    prf.updated_date.timestamp()) + '.png'
                with open(location + '/' + promo_sub_img_filename, "wb") as f:
                    f.write(base64.b64decode(prf.sub_image[23:]))
                    f.close()
                    prf.sub_image = base_url + '/' + promo_sub_img_filename
                prf.save()
