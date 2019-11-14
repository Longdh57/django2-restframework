from rest_framework import serializers
from django.utils import formats

from .models import Merchant
from ..qr_status.models import QrStatus
from ..staff.models import Staff


class MerchantSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    merchant_cube = serializers.SerializerMethodField()
    count_shop = serializers.SerializerMethodField()

    def get_status(self, merchant):
        status = QrStatus.objects.filter(type='MERCHANT', code=merchant.status).first()
        if status is None:
            return '<span class="badge badge-dark">Khác</span>'
        switcher = {
            -1: '<span class="badge badge-danger">' + status.description + '</span>',
            1: '<span class="badge badge-success">' + status.description + '</span>',
            2: '<span class="badge badge-secondary">' + status.description + '</span>',
            3: '<span class="badge badge-warning">' + status.description + '</span>',
            4: '<span class="badge badge-primary">' + status.description + '</span>',
            5: '<span class="badge badge-danger">' + status.description + '</span>',
            6: '<span class="badge badge-danger">' + status.description + '</span>'
        }
        return switcher.get(status.code, '<span class="badge badge-dark">Khác</span>')

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
            'id', 'merchant_code', 'merchant_brand', 'merchant_name', 'merchant_type', 'address',
            'description', 'status', 'department', 'staff', 'created_date', 'modify_date', 'is_care',
            'un_care_date', 'merchant_cube', 'count_shop'
        )
