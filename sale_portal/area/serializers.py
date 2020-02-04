from rest_framework import serializers

from sale_portal.area.models import Area
from sale_portal.administrative_unit.models import QrProvince


class AreaSerializer(serializers.ModelSerializer):
    provinces = serializers.SerializerMethodField()
    proportion_kpi_team = serializers.SerializerMethodField()

    def get_provinces(self, area):
        province_code_lists = area.provinces.split(',')
        data = QrProvince.objects.filter(province_code__in=province_code_lists).values('province_name')
        return data

    def get_proportion_kpi_team(self, area):
        data = area.proportion_kpi.all().values('type', 'leader_coefficient')
        return data

    class Meta:
        model = Area
        fields = (
            'id', 'name', 'code', 'provinces', 'proportion_kpi_team'
        )
