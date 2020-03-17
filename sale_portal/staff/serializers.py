from rest_framework import serializers
from django.utils import formats

from sale_portal.staff.models import Staff
from sale_portal.shop import ShopActivateType
from sale_portal.staff_care import StaffCareType


class StaffSerializer(serializers.ModelSerializer):
    created_date = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    count_shop = serializers.SerializerMethodField()

    def get_created_date(self, staff):
        return formats.date_format(staff.created_date, "SHORT_DATETIME_FORMAT") if staff.created_date else ''

    def get_team(self, staff):
        return staff.team.code if staff.team else ''

    def get_role(self, staff):
        return staff.get_role_name()

    def get_count_shop(self, staff):
        return staff.staff_cares.filter(
            type=StaffCareType.STAFF_SHOP,
            shop__activated = ShopActivateType.ACTIVATE
        ).count()

    class Meta:
        model = Staff
        fields = (
            'id',
            'staff_code',
            'full_name',
            'email',
            'mobile',
            'status',
            'created_date',
            'team',
            'role',
            'count_shop'
        )
