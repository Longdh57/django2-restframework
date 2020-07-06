from rest_framework import serializers

from sale_portal.pos365 import Pos365ContractDuration
from sale_portal.config_kpi.models import ExchangePointPos365


class ExchangePointPos365Serializer(serializers.ModelSerializer):

    class Meta:
        model = ExchangePointPos365
        fields = (
            'id', 'name', 'type', 'point'
        )
