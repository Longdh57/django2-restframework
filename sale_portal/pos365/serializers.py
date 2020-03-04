from rest_framework import serializers
from django.utils import formats

from sale_portal.config_kpi.models import ExchangePointPos365
from sale_portal.pos365.models import Pos365


class Pos365Serializer(serializers.ModelSerializer):
    contract_start_date = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()

    def get_contract_start_date(self, pos365):
        return formats.date_format(pos365.contract_start_date, "SHORT_DATETIME_FORMAT") \
            if pos365.contract_start_date else ''

    def get_staff(self, pos365):
        return pos365.staff.email

    def get_team(self, pos365):
        if pos365.team is not None:
            return pos365.team.name
        return None

    def get_point(self, pos365):
        try:
            if pos365.contract_duration is not None:
                return ExchangePointPos365.objects.get(type=pos365.contract_duration).point
            return 0
        except Exception as e:
            return 0


    class Meta:
        model = Pos365
        fields = (
            'id',
            'code',
            'name',
            'contract_duration',
            'customer_name',
            'staff',
            'team',
            'point',
            'contract_start_date'
        )
