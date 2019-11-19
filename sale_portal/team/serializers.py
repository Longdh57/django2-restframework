from rest_framework import serializers
from django.utils import formats

from .models import Team
from ..shop.models import Shop


class TeamSerializer(serializers.ModelSerializer):
    created_date = serializers.SerializerMethodField()
    count_staff = serializers.SerializerMethodField()
    count_shop = serializers.SerializerMethodField()

    def get_count_staff(self, team):
        return team.staff_set.count()

    def get_count_shop(self, team):
        staffs = team.staff_set.all()
        return Shop.objects.filter(staff__in=staffs).count()

    def get_created_date(self, team):
        return formats.date_format(team.created_date, "SHORT_DATETIME_FORMAT") if team.created_date else ''

    class Meta:
        model = Team
        fields = (
            'id', 'name', 'code', 'description', 'created_date', 'count_staff', 'count_shop'
        )
