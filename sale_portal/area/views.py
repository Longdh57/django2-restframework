from django.db.models import Q
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view

from sale_portal.area.models import Area
from sale_portal.area.serializers import AreaSerializer
from sale_portal.utils.field_formatter import format_string
from sale_portal.administrative_unit.models import QrProvince
from sale_portal.common.standard_response import successful_response


class AreaViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    """
        API get list Area \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
        - province -- text
    """
    serializer_class = AreaSerializer

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


@login_required
@api_view(['GET'])
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
