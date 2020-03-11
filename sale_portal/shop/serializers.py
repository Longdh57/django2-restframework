import ast

from django.utils import formats
from rest_framework import serializers

from ..merchant.models import Merchant
from ..shop.models import Shop


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
    district_name = serializers.SerializerMethodField()
    ward_name = serializers.SerializerMethodField()
    street = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
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

    def get_district_name(self, shop):
        return shop.district.district_name if shop.district else ''

    def get_ward_name(self, shop):
        return shop.wards.wards_name if shop.wards else ''

    def get_street(self, shop):
        return shop.street if shop.street else ''

    def get_address(self, shop):
        return shop.address if shop.address else ''

    def get_created_date(self, shop):
        return formats.date_format(shop.created_date, "SHORT_DATE_FORMAT") if shop.created_date else ''

    def get_count_terminals(self, shop):
        return shop.terminals.count()

    def get_shop_cube(self, shop):
        shop_cube = shop.shop_cube

        if shop_cube is None:
            return None

        voucher_code_list = None
        if shop.shop_cube.voucher_code_list is not None and shop.shop_cube.voucher_code_list != '[]':
            if '[' not in shop.shop_cube.voucher_code_list:
                voucher_code_list = shop.shop_cube.voucher_code_list
            else:
                voucher_code_list = ast.literal_eval(shop.shop_cube.voucher_code_list)

        return {
            'report_date': shop.shop_cube.report_date,
            'number_of_tran': shop.shop_cube.number_of_tran,
            'number_of_tran_w_1_7': shop.shop_cube.number_of_tran_w_1_7,
            'number_of_tran_w_8_14': shop.shop_cube.number_of_tran_w_8_14,
            'number_of_tran_w_15_21': shop.shop_cube.number_of_tran_w_15_21,
            'number_of_tran_w_22_end': shop.shop_cube.number_of_tran_w_22_end,
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
            'district_name',
            'ward_name',
            'street',
            'address',
            'activated',
            'created_date',
            'count_terminals',
            'shop_cube'
        )
