from django.utils import formats
from rest_framework import serializers

from sale_portal.merchant.models import Merchant


class MerchantSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    province_name = serializers.SerializerMethodField()
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

    def get_province_name(self, merchant):
        province = merchant.province
        return province.province_name if province else ''

    def get_staff_care(self, merchant):
        staff_care = merchant.staff_care
        return {
            "full_name": staff_care.full_name,
            "email": staff_care.email,
            "team": staff_care.team.name if staff_care.team else 'N/A',
        } if staff_care else ''

    def get_created_date(self, merchant):
        return formats.date_format(merchant.created_date, "SHORT_DATE_FORMAT") if merchant.created_date else ''

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
            'province_name',
            'staff_care',
            'created_date',
            'modify_date',
            'is_care',
            'un_care_date',
            'merchant_cube',
            'count_ter'
        )
