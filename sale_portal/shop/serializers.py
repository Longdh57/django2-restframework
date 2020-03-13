import ast

from django.utils import formats
from rest_framework import serializers

from sale_portal.shop.models import Shop
from sale_portal.merchant.models import Merchant
from sale_portal.administrative_unit.models import QrProvince, QrDistrict, QrWards


class MerchantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Merchant
        fields = (
            'id', 'merchant_code', 'merchant_brand'
        )


class ShopSerializer(serializers.ModelSerializer):
    merchant = MerchantSerializer()
    staff = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    count_terminals = serializers.SerializerMethodField()
    shop_cube = serializers.SerializerMethodField()

    def get_staff(self, shop):
        team = None
        staff = shop.staff
        if staff is not None:
            team = staff.team
        return {
            'staff_id': staff.id if staff else '',
            'email': staff.email if staff else '',
            'team': {
                'name': team.name if team else '',
                'code': team.code if team else ''
            }
        }

    def get_province_name(self, shop):
        return shop.province.province_name if shop.province else ''

    def get_created_date(self, shop):
        return formats.date_format(shop.created_date, "SHORT_DATE_FORMAT") if shop.created_date else ''

    def get_count_terminals(self, shop):
        return shop.terminals.count()

    def get_shop_cube(self, shop):
        shop_cube = shop.shop_cube

        if shop_cube is None:
            return None

        voucher_code_list = None
        if shop_cube.voucher_code_list is not None and shop_cube.voucher_code_list != '[]':
            if '[' not in shop_cube.voucher_code_list:
                voucher_code_list = shop_cube.voucher_code_list
            else:
                voucher_code_list = ast.literal_eval(shop_cube.voucher_code_list)

        return {
            'report_date': shop_cube.report_date,
            'number_of_tran': shop_cube.number_of_tran,
            'number_of_tran_w_1_7': shop_cube.number_of_tran_w_1_7,
            'number_of_tran_w_8_14': shop_cube.number_of_tran_w_8_14,
            'number_of_tran_w_15_21': shop_cube.number_of_tran_w_15_21,
            'number_of_tran_w_22_end': shop_cube.number_of_tran_w_22_end,
            'voucher_code_list': voucher_code_list,
        }

    class Meta:
        model = Shop
        fields = (
            'id',
            'name',
            'code',
            'merchant',
            'staff',
            'province_name',
            'street',
            'address',
            'activated',
            'created_date',
            'count_terminals',
            'shop_cube'
        )
