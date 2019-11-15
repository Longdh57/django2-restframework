from rest_framework import serializers
from django.utils import formats

from .models import Merchant


class MerchantSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    merchant_cube = serializers.SerializerMethodField()
    count_ter = serializers.SerializerMethodField()

    def get_status(self, merchant):
        return merchant.get_status()

    def get_staff(self, merchant):
        staff = merchant.get_staff()
        return staff.full_name if staff else ''

    def get_created_date(self, merchant):
        return formats.date_format(merchant.created_date, "SHORT_DATETIME_FORMAT") if merchant.created_date else ''

    def get_merchant_cube(self, merchant):
        return merchant.get_merchant_cube()

    def get_count_ter(self, merchant):
        return merchant.terminals.count()

    class Meta:
        model = Merchant
        fields = (
            'id', 'merchant_code', 'merchant_brand', 'merchant_name', 'merchant_type', 'address',
            'description', 'status', 'department', 'staff', 'created_date', 'modify_date', 'is_care',
            'un_care_date', 'merchant_cube', 'count_ter'
        )
