from rest_framework import serializers
from django.utils import formats

from sale_portal.config_kpi.models import ExchangePointPos365
from sale_portal.pos365.models import Pos365
from sale_portal.administrative_unit.models import QrProvince


class ProvinceSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = QrProvince
        fields = (
            'id', 'province_code', 'province_name'
        )


class Pos365Serializer(serializers.ModelSerializer):
    contract_start_date = serializers.SerializerMethodField()
    staff = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()
    area = serializers.SerializerMethodField()
    point = serializers.SerializerMethodField()
    customer_province = ProvinceSerializer()

    def get_contract_start_date(self, pos365):
        return formats.date_format(pos365.contract_start_date, "SHORT_DATE_FORMAT") \
            if pos365.contract_start_date else ''

    def get_staff(self, pos365):
        return pos365.staff.email

    def get_team(self, pos365):
        if pos365.team is not None:
            return pos365.team.name
        return None

    def get_area(self, pos365):
        if pos365.area is not None:
            return pos365.area.name
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
            'contract_product',
            'contract_url',
            'staff',
            'team',
            'area',
            'point',
            'contract_start_date',
            'customer_merchant',
            'customer_name',
            'customer_province'
        )
