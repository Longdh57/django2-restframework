from django.db.models import Q
from datetime import datetime

from rest_framework import viewsets
from .serializers import TerminalSerializer
from .models import Terminal
from ..utils.field_formatter import format_string
from ..shop.models import Shop
from ..staff.models import Staff


class TerminalViewSet(viewsets.ModelViewSet):
    serializer_class = TerminalSerializer

    def get_queryset(self):

        queryset = Terminal.objects.all()

        terminal_id = self.request.query_params.get('terminal_id', None)
        merchant_id = self.request.query_params.get('merchant_id', None)
        staff_id = self.request.query_params.get('staff_id', None)
        team_id = self.request.query_params.get('team_id', None)
        status = self.request.query_params.get('status', None)
        province_code = self.request.query_params.get('province_id', None)
        district_code = self.request.query_params.get('district_id', None)
        ward_code = self.request.query_params.get('ward_id', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if terminal_id is not None and terminal_id != '':
            terminal_id = format_string(terminal_id)
            queryset = queryset.filter(Q(terminal_id__icontains=terminal_id) | Q(terminal_name__icontains=terminal_id))

        if merchant_id is not None and merchant_id != '':
            queryset = queryset.filter(merchant_id=merchant_id)

        if staff_id is not None and staff_id != '':
            shops = Shop.objects.filter(staff=staff_id)
            queryset = queryset.filter(shop__in=shops)

        if team_id is not None and team_id != '':
            staffs = Staff.objects.filter(team_id=team_id)
            shops = Shop.objects.filter(staff__in=staffs)
            queryset = queryset.filter(shop__in=shops)

        if status is not None and status != '':
            queryset = queryset.filter(status=int(status))

        if province_code is not None and province_code != '':
            queryset = queryset.filter(province_code=province_code)

        if district_code is not None and district_code != '':
            queryset = queryset.filter(district_code=district_code)

        if ward_code is not None and ward_code != '':
            queryset = queryset.filter(wards_code=ward_code)

        if from_date is not None and from_date != '':
            queryset = queryset.filter(
                created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))

        if to_date is not None and to_date != '':
            queryset = queryset.filter(
                created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

        return queryset
