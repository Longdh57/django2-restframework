from rest_framework import serializers
from django.utils import formats

from .models import Merchant
from ..staff.models import Staff


class MerchantSerializer(serializers.ModelSerializer):
    staff = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    merchant_cube = serializers.SerializerMethodField()
    count_shop = serializers.SerializerMethodField()

    def get_staff(self, merchant):
        if merchant.staff is not None:
            staff = Staff.objects.filter(pk = merchant.staff).first()
            return staff.full_name if staff else ''
        return ''

    def get_created_date(self, merchant):
        return formats.date_format(merchant.created_date, "SHORT_DATETIME_FORMAT") if merchant.created_date else ''

    def get_merchant_cube(self, merchant):
        return None

    def get_count_shop(self, merchant):
        return 0

    class Meta:
        model = Merchant
        fields = (
            'merchant_code', 'merchant_brand', 'merchant_name', 'merchant_type', 'address',
            'description', 'status', 'department', 'staff', 'created_date', 'modify_date', 'is_care',
            'un_care_date', 'merchant_cube', 'count_shop'
        )
