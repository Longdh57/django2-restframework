import os
import time
import datetime
import xlsxwriter
from datetime import date
from django.db.models import Q
from django.conf import settings
from django.utils import formats
from django.utils import timezone
from django.core.mail import EmailMessage
from datetime import datetime as datedatetime
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from sale_portal.shop.models import Shop
from sale_portal.user.models import User
from sale_portal.shop import ShopActivateType
from sale_portal.terminal.models import Terminal
from sale_portal.cronjob.models import CronjobLog
from sale_portal.utils.excel_util import check_or_create_excel_folder


class Command(BaseCommand):
    help = 'Update mapping shop with terminal daily'

    def get_count_shop_need_update(self):
        shops = Terminal.objects.filter(Q(shop_id__isnull=False)).exclude(status__exact=-1).values('shop_id')
        count = Shop.objects.filter(activated=ShopActivateType.ACTIVATE).exclude(id__in=shops).count()
        return count

    def get_first_date_of_previous_month(self):
        now = time.localtime()
        last = datetime.date(now.tm_year, now.tm_mon, 1) - datetime.timedelta(1)
        first_date_of_last_month = last.replace(day=1)
        return first_date_of_last_month

    def get_shop_is_disabled_from_previous_month(self):
        first_date_of_last_month = self.get_first_date_of_previous_month()

        shops = Shop.objects.filter(activated=0, inactivated_date__gte=first_date_of_last_month).values(
            'code',
            'address',
            'merchant__merchant_brand',
            'created_date',
            'inactivated_date'
        ).order_by('-id')

        return shops

    def get_shop_is_disabled_in_current_month(self):
        shops = Shop.objects.filter(
            activated=0,
            inactivated_date__gte=timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)).values(
            'code',
            'merchant__merchant_brand',
            'created_date',
            'inactivated_date'
        ).order_by('-inactivated_date')

        return shops

    def render_excel_disabled_shop(self, return_url=True):
        check_or_create_excel_folder()
        if not os.path.exists(settings.MEDIA_ROOT + '/excel/disabled-shop'):
            os.mkdir(os.path.join(settings.MEDIA_ROOT + '/excel', 'disabled-shop'))

        file_name = 'disabled-shop_' + date.today().strftime("%d-%m-%Y") + '.xlsx'
        workbook = xlsxwriter.Workbook(settings.MEDIA_ROOT + '/excel/disabled-shop/' + file_name)
        worksheet = workbook.add_worksheet()

        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#74beff',
            'font_color': '#ffffff',
        })

        worksheet.write('A1', 'ID cửa hàng', merge_format)
        worksheet.write('B1', 'Địa chỉ', merge_format)
        worksheet.write('C1', 'Merchant Brand', merge_format)
        worksheet.write('D1', 'Ngày tạo', merge_format)
        worksheet.write('E1', 'Ngày hủy', merge_format)

        shops = self.get_shop_is_disabled_from_previous_month()
        row_num = 1
        for shop in shops:
            row_num += 1
            worksheet.write(row_num, 0, shop['code'])
            worksheet.write(row_num, 1, shop['address'])
            worksheet.write(row_num, 2, shop['merchant__merchant_brand'])
            worksheet.write(row_num, 3, formats.date_format(shop['created_date'], "SHORT_DATETIME_FORMAT") if shop[
                'created_date'] else '')
            worksheet.write(row_num, 4, formats.date_format(shop['inactivated_date'], "SHORT_DATETIME_FORMAT") if shop[
                'inactivated_date'] else '')
        workbook.close()

        if return_url:
            return settings.MEDIA_URL + '/excel/disabled-shop/' + file_name
        return settings.MEDIA_ROOT + '/excel/disabled-shop/' + file_name

    def get_list_email(self):
        user = User.objects.filter(send_disable_shop_email=True)
        emails = [u.email for u in user]
        return emails

    def handle(self, *args, **options):

        name = 'update_mapping_shop_terminal'
        type = 'terminal'

        cron_log = CronjobLog(
            name=name,
            type=type
        )
        cron_log.save()

        try:
            self.stdout.write(self.style.SUCCESS('START PROCESSING...'))

            self.stdout.write('Start set shop_id = null where terminal has status = -1 ...')
            for terminal in Terminal.objects.filter(status=-1, shop_id__isnull=False).all():
                terminal.shop = None
                terminal.save()
            self.stdout.write('Success set shop_id = null where terminal has status = -1')

            self.stdout.write('Start set activated = 0 với shop không có terminal nào...')
            if self.get_count_shop_need_update() != 0:
                shop_activates = Terminal.objects.filter(
                    Q(shop_id__isnull=False),
                    ~Q(status=-1)).all().values('shop_id')
                list_shop_to_disable = Shop.objects.shop_active().filter(~Q(pk__in=shop_activates)).all()
                for shop in list_shop_to_disable:
                    if shop is not None and shop.staff is not None:
                        shop.activated = ShopActivateType.DISABLE
                        shop.save()
                        shop.staff_delete()
            self.stdout.write('Success - Đã set activated = 0 với shop không có terminal !')

            self.stdout.write('Start send email to Sale Manager... !')
            file_path = self.render_excel_disabled_shop(return_url=False)
            datetime_now = datedatetime.now()
            ctx = {
                'current_month': datetime_now.month,
                'previous_month': (datetime_now.month - 1) if (datetime_now.month - 1) != 0 else 12,
                'shops': self.get_shop_is_disabled_in_current_month()
            }
            html_message = render_to_string('shop/mail_template/disable_shop_list.html', ctx)
            mail = EmailMessage(
                '[SALE PORTAL] - Danh sách cửa hàng bị DISSABLE ngày ' + date.today().strftime("%d/%m/%Y"),
                html_message,
                settings.EMAIL_HOST_USER,
                self.get_list_email()
            )
            mail.content_subtype = 'html'
            mail.attach_file(file_path)
            mail.send()
            self.stdout.write('Success - Send email to Sale Manager !')

            self.stdout.write(self.style.SUCCESS('FINISH PROCESSING!'))

            cron_log.status = 1

            cron_log.save()

        except Exception as e:
            cron_log.status = 2
            cron_log.description = str(e)
            cron_log.save()
