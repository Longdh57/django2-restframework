from rest_framework import serializers
from django.utils import formats

from sale_portal.merchant.models import Merchant


class MerchantSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    staff_care = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    merchant_cube = serializers.SerializerMethodField()
    count_ter = serializers.SerializerMethodField()

    def get_status(self, merchant):
        return merchant.get_status()

    def get_staff(self, merchant):
        staff = merchant.get_staff()
        return {
            "full_name": staff.full_name,
            "email": staff.email,
        } if staff else ''

    def get_staff_care(self, merchant):
        staff_care = merchant.staff_care
        return {
            "full_name": staff_care.full_name,
            "email": staff_care.email,
        } if staff_care else ''

    def get_created_date(self, merchant):
        return formats.date_format(merchant.created_date, "SHORT_DATETIME_FORMAT") if merchant.created_date else ''

    def get_merchant_cube(self, merchant):
        return merchant.get_merchant_cube()

    def get_count_ter(self, merchant):
        return merchant.terminals.count()

    class Meta:
        model = Merchant
        fields = (
            'id',
            'merchant_code',
            'merchant_brand',
            'merchant_name',
            'merchant_type',
            'address',
            'description',
            'status',
            'department',
            'staff',
            'staff_care',
            'created_date',
            'modify_date',
            'is_care',
            'un_care_date',
            'merchant_cube',
            'count_ter'
        )
