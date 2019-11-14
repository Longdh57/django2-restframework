from rest_framework import serializers
from django.utils import formats

from .models import Merchant
from ..qr_status.models import QrStatus
from ..staff.models import Staff
from ..shop_cube.models import ShopCube


class MerchantSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    merchant_cube = serializers.SerializerMethodField()
    count_ter = serializers.SerializerMethodField()

    def get_status(self, merchant):
        status = QrStatus.objects.filter(type='MERCHANT', code=merchant.status).first()
        if status is None:
            return '<span class="badge badge-dark">Khác</span>'
        switcher = {
            -1: '<span class="badge badge-danger">' + status.description + '</span>',
            1: '<span class="badge badge-success">' + status.description + '</span>',
            2: '<span class="badge badge-secondary">' + status.description + '</span>',
            3: '<span class="badge badge-warning">' + status.description + '</span>',
            4: '<span class="badge badge-primary">' + status.description + '</span>',
            5: '<span class="badge badge-danger">' + status.description + '</span>',
            6: '<span class="badge badge-danger">' + status.description + '</span>'
        }
        return switcher.get(status.code, '<span class="badge badge-dark">Khác</span>')

    def get_staff(self, merchant):
        if merchant.staff is not None:
            staff = Staff.objects.filter(pk = merchant.staff).first()
            return staff.full_name if staff else ''
        return ''

    def get_created_date(self, merchant):
        return formats.date_format(merchant.created_date, "SHORT_DATETIME_FORMAT") if merchant.created_date else ''

    def get_merchant_cube(self, merchant):
        shops = merchant.shops.values('id')
        shop_cubes = ShopCube.objects.filter(shop_id__in=shops)

        merchant_cube = {
            'number_of_tran_7d': 0,
            'number_of_tran_acm': 0,
            'value_of_tran_7d': 0,
            'value_of_tran_acm': 0,
            'number_of_new_customer': 0,
            'number_of_tran': 0,
            'value_of_tran': 0,
            'number_of_tran_30d': 0
        }
        for shop_cube in shop_cubes:
            merchant_cube.update(
                number_of_tran_7d=merchant_cube.get('number_of_tran_7d') + shop_cube.number_of_tran_7d,
                number_of_tran_acm=merchant_cube.get('number_of_tran_acm') + shop_cube.number_of_tran_acm,
                value_of_tran_7d=merchant_cube.get('value_of_tran_7d') + int(shop_cube.value_of_tran_7d),
                value_of_tran_acm=merchant_cube.get('value_of_tran_acm') + int(shop_cube.value_of_tran_acm),
                number_of_new_customer=merchant_cube.get('number_of_new_customer') + int(
                    shop_cube.number_of_new_customer),
                number_of_tran=merchant_cube.get('number_of_tran') + int(shop_cube.number_of_tran),
                value_of_tran=merchant_cube.get('value_of_tran') + int(shop_cube.value_of_tran),
                number_of_tran_30d=merchant_cube.get('number_of_tran_30d') + int(shop_cube.number_of_tran_30d),
            )
        return merchant_cube

    def get_count_ter(self, merchant):
        return merchant.terminals.count()

    class Meta:
        model = Merchant
        fields = (
            'id', 'merchant_code', 'merchant_brand', 'merchant_name', 'merchant_type', 'address',
            'description', 'status', 'department', 'staff', 'created_date', 'modify_date', 'is_care',
            'un_care_date', 'merchant_cube', 'count_ter'
        )
