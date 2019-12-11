from django.utils import formats
from rest_framework import serializers

from ..merchant.models import Merchant
from ..team.models import Team
from ..staff.models import Staff
from ..shop.models import Shop


class MerchantSerializer(serializers.ModelSerializer):
    merchant = serializers.IntegerField(read_only=True)

    class Meta:
        model = Merchant
        fields = (
            'merchant', 'merchant_name', 'merchant_code', 'merchant_brand'
        )


class TeamSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Team
        fields = (
            'id', 'name', 'code'
        )


class StaffSerializer(serializers.ModelSerializer):
    staff = serializers.IntegerField(read_only=True)

    class Meta:
        model = Staff
        fields = (
            'staff', 'full_name', 'staff_code'
        )


class ShopSerializer(serializers.ModelSerializer):
    # merchant = MerchantSerializer()
    # team = serializers.SerializerMethodField()
    # staff = StaffSerializer()
    # street = serializers.SerializerMethodField()
    # address = serializers.SerializerMethodField()
    # status = serializers.SerializerMethodField()
    # take_care_status = serializers.SerializerMethodField()
    # merchant_name = serializers.SerializerMethodField()
    # merchant_code = serializers.SerializerMethodField()
    # province_id = serializers.SerializerMethodField()
    # district_id = serializers.SerializerMethodField()
    # ward_id = serializers.SerializerMethodField()
    # staff_id = serializers.SerializerMethodField()
    # created_date = serializers.SerializerMethodField()
    # count_terminals = serializers.SerializerMethodField()
    # shop_cube = serializers.SerializerMethodField()

    # def get_merchant_name(self, shop):
    #     return shop.merchant.merchant_name
    #
    # def get_merchant_code(self, shop):
    #     return shop.merchant.merchant_code
    #
    # def get_team(self, shop):
    #     team = shop.get_team()
    #     if team is not None:
    #         team = {
    #             'id': team.id,
    #             'name': team.name,
    #             'code': team.code,
    #         }
    #     return team
    #
    # def get_province_id(self, shop):
    #     return shop.province.province_name if shop.province else ''
    #
    # def get_district_id(self, shop):
    #     return shop.district.district_name if shop.district else ''
    #
    # def get_ward_id(self, shop):
    #     return shop.wards.wards_name if shop.wards else ''
    #
    # def get_staff_id(self, shop):
    #     return shop.staff.email if shop.staff else ''
    #
    # def get_street(self, shop):
    #     return shop.street if shop.street else ''
    #
    # def get_address(self, shop):
    #     return shop.address if shop.address else ''
    #
    # def get_status(self, shop):
    #     return shop.status
    #
    # def get_take_care_status(self, shop):
    #     return shop.get_take_care_status()
    #
    # def get_created_date(self, shop):
    #     return formats.date_format(shop.created_date, "SHORT_DATETIME_FORMAT") if shop.created_date else ''
    #
    # def get_count_terminals(self, shop):
    #     return shop.terminal_set.count()

    # def get_shop_cube(self, shop):
    #     shop_cube = shop.get_shop_cube()
    #     voucher_code_list = ''
    #
    #     if shop_cube is None:
    #         return None
    #
    #     if shop_cube.voucher_code_list is not None and shop_cube.voucher_code_list != '[]':
    #         data = ast.literal_eval(shop_cube.voucher_code_list)
    #         for item in data:
    #             voucher_code_list = voucher_code_list + ' ' + item
    #
    #     return {
    #         'number_of_tran_7d': '{:,}'.format(shop_cube.number_of_tran_7d),
    #         'number_of_new_customer': '{:,}'.format(shop_cube.number_of_new_customer),
    #         'number_of_tran': '{:,}'.format(shop_cube.number_of_tran),
    #         'number_of_tran_30d': '{:,}'.format(shop_cube.number_of_tran_30d),
    #         'number_of_tran_acm': '{:,}'.format(shop_cube.number_of_tran_acm),
    #         'value_of_tran': '{:,}'.format(int(shop_cube.value_of_tran)),
    #         'value_of_tran_7d': '{:,}'.format(int(shop_cube.value_of_tran_7d)),
    #         'value_of_tran_acm': '{:,}'.format(int(shop_cube.value_of_tran_acm)),
    #         'report_date': shop_cube.report_date,
    #         'number_of_tran_w_1_7': '{:,}'.format(shop_cube.number_of_tran_w_1_7),
    #         'number_of_tran_w_8_14': '{:,}'.format(shop_cube.number_of_tran_w_8_14),
    #         'number_of_tran_w_15_21': '{:,}'.format(shop_cube.number_of_tran_w_15_21),
    #         'number_of_tran_w_22_end': '{:,}'.format(shop_cube.number_of_tran_w_22_end),
    #         'number_of_tran_last_month': shop_cube.number_of_tran_last_m_w_1_7 + shop_cube.number_of_tran_last_m_w_8_14
    #                                      + shop_cube.number_of_tran_last_m_w_15_21 + shop_cube.number_of_tran_last_m_w_22_end,
    #         'point_w_1_7': shop_cube.point_w_1_7,
    #         'point_w_8_14': shop_cube.point_w_8_14,
    #         'point_w_15_21': shop_cube.point_w_15_21,
    #         'point_w_22_end': shop_cube.point_w_22_end,
    #         'bonus_point_this_m': shop_cube.bonus_point_this_m,
    #         'voucher_code_list': voucher_code_list,
    #     }

    class Meta:
        model = Shop
        fields = (
            'id', 'name', 'code')

