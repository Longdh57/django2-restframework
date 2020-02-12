from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required

from rest_framework.decorators import api_view
from unidecode import unidecode

from sale_portal.utils.field_formatter import format_string
from sale_portal.common.standard_response import successful_response
from sale_portal.administrative_unit.models import QrProvince, QrDistrict, QrWards


@api_view(['GET'])
@login_required
def list_provinces(request):
    """
        API get list Province to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - code -- text
    """
    queryset = QrProvince.objects.values('id', 'province_code', 'province_name')
    code = request.GET.get('code', None)

    if code is not None and code != '':
        code = unidecode(format_string(code))
        queryset = queryset.filter(Q(province_name__unaccent__icontains=code) | Q(province_code__icontains=code))

    queryset = queryset.order_by('province_name')[0:settings.PAGINATE_BY]

    data = [{
        'id': province['id'],
        'code': province['province_code'],
        'name': province['province_name']
    } for province in queryset]

    return successful_response(data)


@api_view(['GET'])
@login_required
def list_districts(request):
    """
        API get list District to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - code -- text
        - province_code -- text
    """
    queryset = QrDistrict.objects.values('id', 'district_code', 'district_name')

    code = request.GET.get('code', None)
    province_code = request.GET.get('province_code', None)

    if code is not None and code != '':
        code = unidecode(format_string(code))
        queryset = queryset.filter(Q(district_name__unaccent__icontains=code) | Q(district_code__icontains=code))
    if province_code is not None and province_code != '':
        province_code = format_string(province_code)
        queryset = queryset.filter(province_code=province_code)

    queryset = queryset.order_by('district_name')[0:settings.PAGINATE_BY]

    data = [{
        'id': district['id'],
        'code': district['district_code'],
        'name': district['district_name']
    } for district in queryset]

    return successful_response(data)


@api_view(['GET'])
@login_required
def list_wards(request):
    """
        API get list Wards to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - code -- text
        - province_code -- text
        - district_code -- text
    """
    queryset = QrWards.objects.values('id', 'wards_code', 'wards_name')

    code = request.GET.get('code', None)
    province_code = request.GET.get('province_code', None)
    district_code = request.GET.get('district_code', None)

    if code is not None and code != '':
        code = unidecode(format_string(code))
        queryset = queryset.filter(Q(wards_name__unaccent__icontains=code) | Q(wards_code__icontains=code))
    if province_code is not None and province_code != '':
        province_code = format_string(province_code)
        queryset = queryset.filter(province_code=province_code)
    if district_code is not None and district_code != '':
        district_code = format_string(district_code)
        queryset = queryset.filter(district_code=district_code)

    queryset = queryset.order_by('wards_name')[0:settings.PAGINATE_BY]

    data = [{
        'id': wards['id'],
        'code': wards['wards_code'],
        'name': wards['wards_name']
    } for wards in queryset]

    return successful_response(data)
