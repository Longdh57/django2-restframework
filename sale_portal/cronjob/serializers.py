from django.utils import formats
from rest_framework import serializers

from .models import CronjobLog


class CronjobLogSerializer(serializers.ModelSerializer):
    created_date = serializers.SerializerMethodField()

    def get_created_date(self, config):
        return formats.date_format(config.created_date, "SHORT_DATETIME_FORMAT") if config.created_date else ''

    class Meta:
        model = CronjobLog
        fields = (
            'id', 'name', 'type', 'status', 'description', 'created_date'
        )
