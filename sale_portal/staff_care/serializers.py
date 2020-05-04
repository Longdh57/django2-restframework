from rest_framework import serializers
from django.utils import formats

from sale_portal.staff.models import Staff
from sale_portal.staff_care.models import StaffCareLog, StaffCareImportLog


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


class StaffSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Staff
        fields = (
            'id', 'full_name', 'email'
        )


class StaffCareLogSerializer(serializers.ModelSerializer):
    staff = StaffSerializer()
    created_date = serializers.SerializerMethodField()
    updated_date = serializers.SerializerMethodField()

    def get_created_date(self, staff_care_log):
        return formats.date_format(staff_care_log.created_date,
                                   "SHORT_DATETIME_FORMAT") if staff_care_log.created_date else ''

    def get_updated_date(self, staff_care_log):
        return formats.date_format(staff_care_log.updated_date,
                                   "SHORT_DATETIME_FORMAT") if staff_care_log.updated_date else ''

    class Meta:
        model = StaffCareLog
        fields = (
            'id',
            'shop',
            'staff',
            'is_caring',
            'created_date',
            'updated_date'
        )
