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
        return terminal.get_staff()

    def get_team(self, terminal):
        return terminal.get_team()

    def get_province_name(self, terminal):
        return terminal.get_province().province_name if terminal.get_province() else ''

    def get_district_name(self, terminal):
        return terminal.get_district().district_name if terminal.get_district() else ''

    def get_ward_name(self, terminal):
        return terminal.get_wards().wards_name if terminal.get_wards() else ''

    def get_created_date(self, terminal):
        return formats.date_format(terminal.created_date, "SHORT_DATETIME_FORMAT") if terminal.created_date else ''

    class Meta:
        model = Terminal
        fields = (
            'terminal_id', 'terminal_name', 'merchant', 'shop', 'staff', 'team', 'terminal_address', 'status',
            'province_name', 'district_name', 'ward_name', 'business_address', 'created_date'
        )
