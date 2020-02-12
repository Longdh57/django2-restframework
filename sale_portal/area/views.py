import logging

from django.db.models import Q
from django.contrib.auth.decorators import login_required, permission_required

from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view

from sale_portal.area.models import Area
from sale_portal.area.serializers import AreaSerializer
from sale_portal.utils.permission import get_user_permission_classes
from sale_portal.utils.field_formatter import format_string
from sale_portal.administrative_unit.models import QrProvince
from sale_portal.common.standard_response import successful_response, custom_response, Code


class AreaViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
        API get list Area \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
        - province -- text
    """
    serializer_class = AreaSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = get_user_permission_classes('area.area_list_data', self.request)
        if self.action == 'retrieve':
            permission_classes = get_user_permission_classes('area.area_detail', self.request)
        if self.action == 'create':
            permission_classes = get_user_permission_classes('area.area_create', self.request)
        if self.action == 'update':
            permission_classes = get_user_permission_classes('area.area_edit', self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = Area.objects.all()

        code = self.request.query_params.get('code', None)
        province = self.request.query_params.get('province', None)

        if code is not None and code != '':
            code = format_string(code)
            queryset = queryset.filter(Q(name__icontains=code) | Q(code__icontains=code))
        if province is not None and province != '':
            province = format_string(province)
            province = QrProvince.objects.filter(province_code=province).first()
            queryset = queryset.filter(provinces__icontains=province)

        return queryset

    def retrieve(self, request, pk):
        """
            API get detail Area
        """
        try:
            area = Area.objects.filter(pk=pk).first()
            if area is None:
                return custom_response(Code.AREA_NOT_FOUND)

            province_lists, proportion_kpi_lists = [], []
            province_code_lists = area.provinces.split(',')
            for item in QrProvince.objects.filter(province_code__in=province_code_lists).values('province_code',
                                                                                                'province_name'):
                province_lists.append({
                    'province_code': item['province_code'],
                    'province_name': item['province_name'],
                })

            for proportion_kpi in area.proportion_kpi.all().values('type', 'leader_coefficient'):
                proportion_kpi_lists.append({
                    'type': proportion_kpi['type'],
                    'leader_coefficient': proportion_kpi['leader_coefficient'],
                })

            data = {
                'name': area.name,
                'code': area.code,
                'provinces': province_lists,
                'proportion_kpi_team': proportion_kpi_lists
            }
            return successful_response(data)
        except Exception as e:
            logging.error('Get detail area exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@login_required
@permission_required('area.area_list_data', raise_exception=True)
def list_areas(request):
    """
        API get list Area to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - code -- text
    """

    queryset = Area.objects.values('id', 'name', 'code')

    code = request.GET.get('code', None)

    if code is not None and code != '':
        queryset = queryset.filter(Q(name__icontains=code) | Q(code__icontains=code))

    queryset = queryset.order_by('name')

    data = [{'id': area['id'], 'name': area['name'] + ' - ' + area['code']} for area in queryset]

    return successful_response(data)
