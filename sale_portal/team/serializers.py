from rest_framework import serializers
from django.utils import formats

from sale_portal.team.models import Team
from sale_portal.shop import ShopActivateType
from sale_portal.staff_care import StaffCareType
from sale_portal.staff_care.models import StaffCare


class TeamSerializer(serializers.ModelSerializer):
    created_date = serializers.SerializerMethodField()
    count_staff = serializers.SerializerMethodField()
    count_shop = serializers.SerializerMethodField()

    def get_count_staff(self, team):
        return team.staff_set.count()

    def get_count_shop(self, team):
        staffs = team.staff_set.all()
        return StaffCare.objects.filter(
            staff__in=staffs,
            type=StaffCareType.STAFF_SHOP,
            shop__activated=ShopActivateType.ACTIVATE
        ).count()

    def get_created_date(self, team):
        return formats.date_format(team.created_date, "SHORT_DATETIME_FORMAT") \
            if team.created_date else ''

    class Meta:
        model = Team
        fields = (
            'id', 'name', 'code', 'description', 'created_date', 'count_staff', 'count_shop'
        )
