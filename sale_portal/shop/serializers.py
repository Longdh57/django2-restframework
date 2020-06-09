import ast

from django.utils import formats
from rest_framework import serializers

from sale_portal.merchant.models import Merchant
from sale_portal.shop import ShopLogType
from sale_portal.shop.models import Shop, ShopFullData, ShopLog


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
            'number_of_tran_acm': shop_cube.number_of_tran_acm,
            'number_of_tran_last_m': shop_cube.number_of_tran_last_m,
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
            'shop_cube',
            'take_care_status'
        )


class ShopFullDataSerializer(serializers.ModelSerializer):
    merchant = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    shop_cube = serializers.SerializerMethodField()

    def get_merchant(self, shop_full_data):
        return {
            'merchant_brand': shop_full_data.merchant_brand,
            'merchant_code': shop_full_data.merchant_code
        }

    def get_staff(self, shop_full_data):
        return {
            'email': shop_full_data.staff_email or '',
            'team': {
                'name': shop_full_data.team_name or '',
            }
        }

    def get_created_date(self, shop_full_data):
        return formats.date_format(shop_full_data.created_date,
                                   "SHORT_DATE_FORMAT") if shop_full_data.created_date else ''

    def get_shop_cube(self, shop_full_data):
        if shop_full_data.number_of_tran is None:
            return None

        voucher_code_list = None
        if shop_full_data.voucher_code_list is not None and shop_full_data.voucher_code_list != '[]':
            if '[' not in shop_full_data.voucher_code_list:
                voucher_code_list = shop_full_data.voucher_code_list
            else:
                voucher_code_list = ast.literal_eval(shop_full_data.voucher_code_list)

        return {
            'report_date': shop_full_data.report_date,
            'number_of_tran_acm': shop_full_data.number_of_tran_acm,
            'number_of_tran_last_m': shop_full_data.number_of_tran_last_m,
            'number_of_tran': shop_full_data.number_of_tran,
            'number_of_tran_w_1_7': shop_full_data.number_of_tran_w_1_7,
            'number_of_tran_w_8_14': shop_full_data.number_of_tran_w_8_14,
            'number_of_tran_w_15_21': shop_full_data.number_of_tran_w_15_21,
            'number_of_tran_w_22_end': shop_full_data.number_of_tran_w_22_end,
            'voucher_code_list': voucher_code_list,
        }

    class Meta:
        model = ShopFullData
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
            'shop_cube',
            'take_care_status'
        )


class ShopLogSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    new_data = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()

    def get_type(self, shop_log):
        types = dict((x, y) for x, y in ShopLogType.CHOICES)
        return types[shop_log.type]

    def get_new_data(self, shop_log):
        return {
            'Tên shop': shop_log.new_data['name'] or None,
            'Đường phố': shop_log.new_data['street'] or None,
            'Địa chỉ': shop_log.new_data['address'] or None,
            'MC_id': shop_log.new_data['merchant_id'] or None,
            'Chăm sóc': shop_log.new_data['take_care_status'] or None,
            'Hoạt động': shop_log.new_data['activated'] or None,
            'Tỉnh/Huyện/Đường phố': str(shop_log.new_data['province_id']) + '/' + str(
                shop_log.new_data['district_id']) + '/' + str(shop_log.new_data['wards_id'])
        }

    def get_created_date(self, shop_log):
        return formats.date_format(shop_log.created_date, "SHORT_DATETIME_FORMAT") if shop_log.created_date else ''

    class Meta:
        model = ShopLog
        fields = (
            'id',
            'shop_id',
            'new_data',
            'type',
            'created_date'
        )
