from django.urls import reverse
from django.utils import formats
from rest_framework import serializers

from ..merchant.models import Merchant
from ..shop.models import Shop
from .models import Terminal


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
    province_name = serializers.SerializerMethodField()
    district_name = serializers.SerializerMethodField()
    ward_name = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()

    def get_status(self, terminal):
        return terminal.get_status()

    def get_staff(self, terminal):
        staff = terminal.get_staff()
        return staff.email if staff else ''

    def get_team(self, terminal):
        team = terminal.get_team()
        return team.code if team else None

    def get_province_name(self, terminal):
        province = terminal.get_province()
        return province.province_name if province else ''

    def get_district_name(self, terminal):
        district = terminal.get_district()
        return district.district_name if district else ''

    def get_ward_name(self, terminal):
        wards = terminal.get_wards()
        return wards.wards_name if wards else ''

    def get_created_date(self, terminal):
        return formats.date_format(terminal.created_date, "SHORT_DATETIME_FORMAT") if terminal.created_date else ''

    class Meta:
        model = Terminal
        fields = (
            'id', 'terminal_id', 'terminal_name', 'merchant', 'shop', 'staff', 'team', 'terminal_address', 'status',
            'province_name', 'district_name', 'ward_name', 'business_address', 'created_date'
        )
