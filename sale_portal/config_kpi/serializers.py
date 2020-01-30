from rest_framework import serializers

from sale_portal.pos365 import Pos365ContractDuration
from sale_portal.config_kpi.models import ExchangePointPos365


class ExchangePointPos365Serializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()

    def get_type(self, exchange_point_pos365):
        return Pos365ContractDuration.CHOICES[exchange_point_pos365.type][1]

    class Meta:
        model = ExchangePointPos365
        fields = (
            'id', 'type', 'point'
        )
