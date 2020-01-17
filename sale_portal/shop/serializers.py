from django.utils import formats
from rest_framework import serializers

from ..merchant.models import Merchant
from ..shop.models import Shop


class MerchantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Merchant
        fields = (
            'id', 'merchant_name', 'merchant_code', 'merchant_brand'
        )


class ShopSerializer(serializers.ModelSerializer):
    merchant = MerchantSerializer()
    staff = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
    street = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    count_terminals = serializers.SerializerMethodField()
    shop_cube = serializers.SerializerMethodField()

    def get_staff(self, shop):
        staff = shop.staff
        return {
            'staff_id': staff.id if staff else '',
            'staff_code': staff.staff_code if staff else '',
            'full_name': staff.full_name if staff else '',
            'email': staff.email if staff else '',
            'team_name': staff.team.name if staff and staff.team else '',
            'team_code': staff.team.code if staff and staff.team else ''
        }

    def get_province_name(self, shop):
        return shop.province.province_name if shop.province else ''

    def get_street(self, shop):
        return shop.street if shop.street else ''

    def get_address(self, shop):
        return shop.address if shop.address else ''

    def get_created_date(self, shop):
        return formats.date_format(shop.created_date, "SHORT_DATETIME_FORMAT") if shop.created_date else ''

    def get_count_terminals(self, shop):
        return shop.terminals.count()

    def get_shop_cube(self, shop):
        shop_cube = shop.shop_cube()
        voucher_code_list = ''

        if shop_cube is None:
            return None

        return {
            'number_of_new_customer': '{:,}'.format(shop_cube.number_of_new_customer),
            'number_of_tran': '{:,}'.format(shop_cube.number_of_tran),
            'number_of_tran_7d': '{:,}'.format(shop_cube.number_of_tran_7d),
            'number_of_tran_30d': '{:,}'.format(shop_cube.number_of_tran_30d),
            'number_of_tran_acm': '{:,}'.format(shop_cube.number_of_tran_acm),
            'number_of_tran_last_month': shop_cube.number_of_tran_last_m_w_1_7 + shop_cube.number_of_tran_last_m_w_8_14
                                         + shop_cube.number_of_tran_last_m_w_15_21 + shop_cube.number_of_tran_last_m_w_22_end,
            'value_of_tran': '{:,}'.format(int(shop_cube.value_of_tran)),
            'value_of_tran_7d': '{:,}'.format(int(shop_cube.value_of_tran_7d)),
            'value_of_tran_acm': '{:,}'.format(int(shop_cube.value_of_tran_acm)),
            'report_date': shop_cube.report_date,
            'number_of_tran_w_1_7': '{:,}'.format(shop_cube.number_of_tran_w_1_7),
            'number_of_tran_w_8_14': '{:,}'.format(shop_cube.number_of_tran_w_8_14),
            'number_of_tran_w_15_21': '{:,}'.format(shop_cube.number_of_tran_w_15_21),
            'number_of_tran_w_22_end': '{:,}'.format(shop_cube.number_of_tran_w_22_end),
            'point_w_1_7': shop_cube.point_w_1_7,
            'point_w_8_14': shop_cube.point_w_8_14,
            'point_w_15_21': shop_cube.point_w_15_21,
            'point_w_22_end': shop_cube.point_w_22_end,
            'bonus_point_this_m': shop_cube.bonus_point_this_m,
        }

    class Meta:
        model = Shop
        fields = (
            'id', 'name', 'code', 'merchant', 'staff', 'province_name', 'street', 'address', 'activated',
            'created_date', 'count_terminals', 'shop_cube')

