from rest_framework import serializers

from sale_portal.area.models import Area
from sale_portal.administrative_unit.models import QrProvince


class AreaSerializer(serializers.ModelSerializer):
    provinces = serializers.SerializerMethodField()

    def get_provinces(self, staff):
        province_code_lists = staff.provinces.split(',')
        data = QrProvince.objects.filter(province_code__in=province_code_lists).values('province_name')
        return data

    class Meta:
        model = Area
        fields = (
            'id', 'name', 'code', 'provinces'
        )
