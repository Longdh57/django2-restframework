from rest_framework import serializers
from django.utils import formats

from .models import Staff


class StaffSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    count_shop = serializers.SerializerMethodField()

    def get_status(self, staff):
        return staff.get_status()

    def get_created_date(self, staff):
        return formats.date_format(staff.created_date, "SHORT_DATETIME_FORMAT") if staff.created_date else ''

    def get_team(self, staff):
        return staff.team.code if staff.team else ''

    def get_count_shop(self, staff):
        return staff.shops.count()

    class Meta:
        model = Staff
        fields = (
            'staff_code', 'full_name', 'email', 'mobile', 'status', 'created_date', 'team', 'count_shop'
        )
