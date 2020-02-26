from django.utils import formats
from rest_framework import serializers

from .models import Terminal
from ..merchant.models import Merchant
from ..shop.models import Shop


class MerchantSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Merchant
        fields = (
            'id', 'merchant_code', 'merchant_name', 'merchant_brand'
        )


class ShopSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Shop
        fields = (
            'id', 'name', 'code', 'address', 'street'
        )


class TerminalSerializer(serializers.ModelSerializer):
    merchant = MerchantSerializer()
    shop = ShopSerializer()
    status = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    province = serializers.SerializerMethodField()
    district = serializers.SerializerMethodField()
    ward = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()

    def get_status(self, terminal):
        return terminal.get_status()

    def get_staff(self, terminal):
        staff = terminal.get_staff()
        return staff.email if staff else ''

    def get_team(self, terminal):
        team = terminal.get_team()
        return team.code if team else ''

    def get_province(self, terminal):
        province = terminal.get_province()
        if province:
            return {
                'id': province.id,
                'code': province.province_code,
                'name': province.province_name
            }
        else:
            return None

    def get_district(self, terminal):
        district = terminal.get_district()
        if district:
            return {
                'id': district.id,
                'code': district.district_code,
                'name': district.district_name
            }
        else:
            return None

    def get_ward(self, terminal):
        ward = terminal.get_wards()
        if ward:
            return {
                'id': ward.id,
                'code': ward.wards_code,
                'name': ward.wards_name
            }
        else:
            return None

    def get_created_date(self, terminal):
        return formats.date_format(terminal.created_date, "SHORT_DATETIME_FORMAT") if terminal.created_date else ''

    class Meta:
        model = Terminal
        fields = (
            'id', 'terminal_id', 'terminal_name', 'merchant', 'shop', 'staff', 'team', 'terminal_address', 'status',
            'province', 'district', 'ward', 'business_address', 'created_date'
        )