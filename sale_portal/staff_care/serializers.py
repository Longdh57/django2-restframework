from rest_framework import serializers
from django.utils import formats

from sale_portal.staff_care.models import StaffCareImportLog


class StaffCareImportLogSerializer(serializers.ModelSerializer):
    description = serializers.SerializerMethodField()
    created_by = serializers.SerializerMethodField()
    created_date = serializers.SerializerMethodField()

    def get_created_date(self, staff_care_import_log):
        return formats.date_format(staff_care_import_log.created_date,
                                   "SHORT_DATETIME_FORMAT") if staff_care_import_log.created_date else ''

    def get_description(self, staff_care_import_log):
        return staff_care_import_log.description

    def get_created_by(self, staff_care_import_log):
        return staff_care_import_log.created_by.email if staff_care_import_log.description else ''

    class Meta:
        model = StaffCareImportLog
        fields = (
            'id',
            'file_url',
            'description',
            'type',
            'created_by',
            'created_date'
        )
