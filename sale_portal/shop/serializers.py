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
    team = serializers.SerializerMethodField()
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
        }

    def get_team(self, shop):
        team = shop.team
        return {
            'name': team.name if team else '',
            'code': team.code if team else ''
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
        shop_cube = shop.shop_cube

        if shop_cube is None:
            return None

        return {
            'report_date': shop.shop_cube.report_date,
            'number_of_tran': int(
                shop.shop_cube.number_of_tran) if shop.shop_cube.number_of_tran.isdigit() else None,
            'number_of_tran_w_1_7': int(
                shop.shop_cube.number_of_tran_w_1_7) if shop.shop_cube.number_of_tran_w_1_7.isdigit() else None,
            'number_of_tran_w_8_14': int(
                shop.shop_cube.number_of_tran_w_8_14) if shop.shop_cube.number_of_tran_w_8_14.isdigit() else None,
            'number_of_tran_w_15_21': int(
                shop.shop_cube.number_of_tran_w_15_21) if shop.shop_cube.number_of_tran_w_15_21.isdigit() else None,
            'number_of_tran_w_22_end': int(
                shop.shop_cube.number_of_tran_w_22_end) if shop.shop_cube.number_of_tran_w_22_end.isdigit() else None,
        }

    class Meta:
        model = Shop
        fields = (
            'id',
            'name',
            'code',
            'merchant',
            'staff',
            'team',
            'province_name',
            'street',
            'address',
            'activated',
            'created_date',
            'count_terminals',
            'shop_cube'
        )
