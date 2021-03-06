from django.utils import formats
from rest_framework import serializers

from .models import SaleReport
from sale_portal.staff.models import Staff


class SaleReportSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    merchant = serializers.SerializerMethodField()
    shop_name = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    updated_date = serializers.SerializerMethodField()

    def get_created_by(self, sale_report):
        staff = Staff.objects.filter(email=sale_report.created_by).first()
        if staff is None:
            return {
                'user_id': sale_report.created_by.id,
                'staff_id': 'N/A',
                'full_name': 'N/A',
                'email': sale_report.created_by.email,
                'team': 'N/A'
            }
        else:
            return {
                'user_id': sale_report.created_by.id,
                'staff_id': staff.id,
                'full_name': staff.full_name,
                'email': staff.email,
                'team': {
                    'id': staff.team.id,
                    'code': staff.team.code,
                    'name': staff.team.name if staff.team.name is not None else 'N/A',
                    'description': staff.team.description if staff.team.description is not None else 'N/A',
                } if staff.team is not None else 'N/A'
            }

    def get_merchant(self, sale_report):
        if sale_report.purpose != 0:
            shop = sale_report.get_shop()
            if shop is not None:
                merchant = shop.merchant
                return {
                    'id': merchant.id,
                    'code': merchant.merchant_code,
                    'brand': merchant.merchant_brand,
                }
        return None

    def get_shop_name(self, sale_report):
        shop = sale_report.get_shop()
        return shop.name if shop else ''

    def get_created_date(self, sale_report):
        return formats.date_format(sale_report.created_date,
                                   "SHORT_DATETIME_FORMAT") if sale_report.created_date else ''

    def get_updated_date(self, sale_report):
        return formats.date_format(sale_report.updated_date,
                                   "SHORT_DATETIME_FORMAT") if sale_report.updated_date else ''

    class Meta:
        model = SaleReport
        fields = (
            'id',
            'purpose',
            'longitude',
            'latitude',
            'created_date',
            'updated_date',
            'created_by',
            'updated_by',
            'new_merchant_name',
            'new_merchant_brand',
            'new_address',
            'new_customer_name',
            'new_phone',
            'new_result',
            'new_using_application',
            'shop_code',
            'shop_status',
            'shop_name',
            'cessation_of_business_note',
            'cessation_of_business_image',
            'customer_care_posm',
            'customer_care_cashier_reward',
            'customer_care_transaction',
            'implement_confirm',
            'implement_posm',
            'implement_merchant_view',
            'implement_career_guideline',
            'merchant'
        )


class SaleReportStatisticSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    full_name = serializers.CharField()
    count_total = serializers.IntegerField()
    count_new = serializers.IntegerField()
    count_impl = serializers.IntegerField()
    count_care = serializers.IntegerField()
    count_new_signed = serializers.IntegerField()
    count_new_unsigned = serializers.IntegerField()
    count_new_consider = serializers.IntegerField()
    count_new_refused = serializers.IntegerField()
    count_care_cessation = serializers.IntegerField()
    count_care_liquidation = serializers.IntegerField()
    count_care_opening = serializers.IntegerField()
    count_care_uncooperative = serializers.IntegerField()
    count_standee_qr = serializers.IntegerField()
    count_sticker_door = serializers.IntegerField()
    count_sticker_table = serializers.IntegerField()
    count_guide = serializers.IntegerField()
    count_wobbler = serializers.IntegerField()
    count_poster = serializers.IntegerField()
    count_standee_ctkm = serializers.IntegerField()
    count_tentcard = serializers.IntegerField()
