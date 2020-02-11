from django.shortcuts import render

from datetime import datetime
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required, permission_required

from sale_portal.pos365.models import Pos365
from sale_portal.pos365 import Pos365ContractDuration
from sale_portal.pos365.serializers import Pos365Serializer
from sale_portal.utils.field_formatter import format_string
from sale_portal.common.standard_response import successful_response


class Pos365ViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list Pos365 \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
    """
    serializer_class = Pos365Serializer

    def get_queryset(self):

        queryset = Pos365.objects.all()

        code = self.request.query_params.get('code', None)
        name = self.request.query_params.get('name', None)
        sale_email = self.request.query_params.get('sale_email', None)
        contract_duration = self.request.query_params.get('contract_duration', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if code is not None and code != '':
            code = format_string(code)
            queryset = queryset.filter(code__icontains=code)
        if name is not None and name != '':
            name = format_string(name)
            queryset = queryset.filter(name__icontains=name)
        if sale_email is not None and sale_email != '':
            sale_email = format_string(sale_email)
            queryset = queryset.filter(staff__email__icontains=sale_email)
        if contract_duration is not None and contract_duration != '':
            contract_duration = int(contract_duration)
            queryset = queryset.filter(contract_duration=contract_duration)
        if from_date is not None and from_date != '':
            queryset = queryset.filter(
                contract_start_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
        if to_date is not None and to_date != '':
            queryset = queryset.filter(
                contract_start_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))
        return queryset


@api_view(['GET'])
@login_required
def list_contract_durations(request):
    """
        API get list thời hạn HĐ
    """
    data = []
    for item in Pos365ContractDuration.CHOICES:
        data.append({"code": item[0], "description": item[1]})

    return successful_response(data)
