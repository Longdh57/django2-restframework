import json, os
import logging
import datetime

from django.db.models import Q
from django.utils import formats
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, get_object_or_404

from time import time
from datetime import datetime as dt_datetime
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required, permission_required

from sale_portal import settings
from sale_portal.administrative_unit.models import QrProvince
from sale_portal.config_kpi.models import ExchangePointPos365
from sale_portal.pos365.models import Pos365
from sale_portal.pos365 import Pos365ContractDuration
from sale_portal.pos365.serializers import Pos365Serializer
from sale_portal.staff.models import Staff
from sale_portal.team.models import Team
from sale_portal.utils.field_formatter import format_string
from sale_portal.common.standard_response import successful_response, custom_response, Code
from sale_portal.utils.queryset import get_staffs_viewable_queryset, get_teams_viewable_queryset


class Pos365ViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list Pos365 \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
    """
    serializer_class = Pos365Serializer

    def get_queryset(self):
        return get_queryset_pos365_list(self.request)

    def create(self, request):
        """
            API create Pos365 \n
            Request body for this api : Định dạng form-data \n
                "code": "IRNARF",
                "name": "Hợp đồng với Canifa",
                "contract_duration": 1, (type in {0,1,2,3,4,5,6,...} )
                "contract_coefficient": 100,
                "staff_id": 1210,
                "contract_team": 1210,
                "contract_start_date": "25/01/2020" (format date in %d/%m/%Y),
                "contract_url": "https://canifa.vn",
                "contract_product": "Phần mềm POS365",
                "contract_file": "",
                "customer_merchant": "Canifa",
                "customer_name": "Đào Hải Long",
                "customer_phone": "038123456",
                "customer_delegate_person": "Long Đào Hải",
                "customer_address": "36 Hoàng Cầu, Q Đống Đa, Hà Nội"
                "customer_province": 1 -- number,
        """
        try:
            data = json.loads(request.POST.get('data'))

            code = data.get('code', None)
            name = data.get('name', None)
            contract_duration = data.get('contract_duration', None)
            contract_coefficient = data.get('contract_coefficient', None)
            staff_id = data.get('staff_id', None)
            is_collaborators = data.get('is_collaborators', None)
            contract_team = data.get('contract_team', None)
            contract_url = data.get('contract_url', None)
            contract_product = data.get('contract_product', None)
            contract_start_date = data.get('contract_start_date', None)
            contract_file = request.FILES['contract_file'] if 'contract_file' in request.FILES else None
            customer_merchant = data.get('customer_merchant', None)
            customer_name = data.get('customer_name', None)
            customer_phone = data.get('customer_phone', None)
            customer_delegate_person = data.get('customer_delegate_person', None)
            customer_address = data.get('customer_address', None)
            customer_province = data.get('customer_province', None)

            if contract_duration is not None and contract_duration != '':
                if not (isinstance(contract_duration, int) or (
                        ExchangePointPos365.objects.filter(pk=contract_duration).count() != 1)):
                    return custom_response(Code.INVALID_BODY, 'contract_duration Invalid')

            if contract_coefficient is not None and contract_coefficient != '':
                if not (isinstance(contract_coefficient, int) and 0 <= contract_coefficient <= 100):
                    return custom_response(Code.INVALID_BODY, 'contract_coefficient Invalid')

            if name is None or name == '' or code is None or code == '':
                return custom_response(Code.INVALID_BODY, 'name or code Invalid')
            name = format_string(name)
            code = format_string(code)

            if Pos365.objects.filter(code__iexact=code):
                return custom_response(Code.BAD_REQUEST, 'code be used by other Pos365')

            if is_collaborators:
                if (not isinstance(contract_team, int)) or (Team.objects.filter(pk=contract_team).count() != 1):
                    return custom_response(Code.TEAM_NOT_FOUND)
                else:
                    contract_team = Team.objects.get(pk=contract_team)
            else:
                if (not isinstance(staff_id, int)) or (Staff.objects.filter(pk=staff_id).count() != 1):
                    return custom_response(Code.STAFF_NOT_FOUND)

            if contract_file is not None:
                fs = FileSystemStorage(
                    location=settings.FS_DOCUMENT_UPLOADS + datetime.date.today().isoformat(),
                    base_url=settings.FS_DOCUMENT_URL + datetime.date.today().isoformat()
                )
                file_type = os.path.splitext(contract_file.name)[1]
                filename = fs.save(str(request.user.username) + str(time()) + file_type, contract_file)
                uploaded_file_url = fs.url(filename)
            else:
                uploaded_file_url = None

            contract_url = format_string(contract_url)
            contract_product = format_string(contract_product)
            contract_start_date = dt_datetime.strptime(contract_start_date[:10], '%Y-%m-%d')

            customer_merchant = format_string(customer_merchant)
            customer_name = format_string(customer_name)
            customer_phone = format_string(customer_phone)
            customer_delegate_person = format_string(customer_delegate_person)
            customer_address = format_string(customer_address)
            province = QrProvince.objects.filter(pk=int(customer_province)).first()
            if not province:
                return custom_response(Code.BAD_REQUEST, 'Wrong Province')

            pos365 = Pos365(
                code=code,
                name=name,
                contract_duration=contract_duration,
                contract_coefficient=contract_coefficient,
                staff_id=staff_id,
                contract_team=contract_team,
                contract_url=contract_url,
                contract_product=contract_product,
                contract_start_date=contract_start_date,
                contract_file=uploaded_file_url,
                customer_merchant=customer_merchant,
                customer_name=customer_name,
                customer_phone=customer_phone,
                customer_delegate_person=customer_delegate_person,
                customer_address=customer_address,
                customer_province=province,
                created_by=request.user,
                updated_by=request.user
            )
            pos365.save()

            return successful_response(pos365.id)

        except Exception as e:
            logging.error('Create pos365 exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)

    def retrieve(self, request, pk):
        pos365 = get_object_or_404(Pos365, pk=pk)
        contract_start_date = formats.date_format(pos365.contract_start_date, "SHORT_DATETIME_FORMAT") \
            if pos365.contract_start_date else ''
        staff = pos365.staff.email if pos365.staff is not None else None
        team = pos365.team.name if pos365.team is not None else None
        if pos365.contract_duration is not None:
            contract_duration_data = ExchangePointPos365.objects.get(type=pos365.contract_duration)
        else:
            contract_duration_data = None
        return successful_response({
            'id': pos365.id,
            'code': pos365.code,
            'name': pos365.name,
            'contract_duration': contract_duration_data.name,
            'contract_url': pos365.contract_url,
            'contract_product': pos365.contract_product,
            'contract_file': {
                'name': os.path.basename(pos365.contract_file.name),
                'url': str(pos365.contract_file.url),
            } if pos365.contract_file else None,
            'staff': staff,
            'team': team,
            'contract_start_date': contract_start_date,
            'contract_coefficient': pos365.contract_coefficient,
            'point': (
                             contract_duration_data.point * pos365.contract_coefficient) / 100 if contract_duration_data else 0,
            'customer_merchant': pos365.customer_merchant,
            'customer_name': pos365.customer_name,
            'customer_phone': pos365.customer_phone,
            'customer_delegate_person': pos365.customer_delegate_person,
            'customer_address': pos365.customer_address,
            'customer_province': pos365.customer_province.province_name if pos365.customer_province else None,

        })


@api_view(['GET'])
@login_required
def list_contract_durations(request):
    """
        API get list thời hạn HĐ
    """
    data = []

    for item in ExchangePointPos365.objects.order_by('id').all():
        data.append({"code": item.type, "description": item.name})

    return successful_response(data)


def get_queryset_pos365_list(request):
    pos365_obj = Pos365

    queryset = pos365_obj.objects.filter(Q(staff__in=get_staffs_viewable_queryset(request.user)) | Q(
        contract_team__in=get_teams_viewable_queryset(request.user)))

    code = request.query_params.get('code', None)
    staff_id = request.query_params.get('staff_id', None)
    contract_duration = request.query_params.get('contract_duration', None)
    province_id = request.query_params.get('province_id', None)
    from_date = request.query_params.get('from_date', None)
    to_date = request.query_params.get('to_date', None)

    if code is not None and code != '':
        code = format_string(code)
        queryset = queryset.filter(code__icontains=code)
    if staff_id is not None and staff_id != '':
        queryset = queryset.filter(staff_id=staff_id)
    if contract_duration is not None and contract_duration != '':
        contract_duration = int(contract_duration)
        queryset = queryset.filter(contract_duration=contract_duration)
    if province_id is not None and province_id != '':
        queryset = queryset.filter(customer_province=province_id)
    if from_date is not None and from_date != '':
        queryset = queryset.filter(
            contract_start_date__gte=dt_datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
    if to_date is not None and to_date != '':
        queryset = queryset.filter(
            contract_start_date__lte=(dt_datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))
    return queryset
