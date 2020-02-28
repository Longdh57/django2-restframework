import json
import logging

from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated

from sale_portal.area.models import Area
from sale_portal.common.standard_response import successful_response, custom_response, Code
from sale_portal.config_kpi import ProportionKpiTeamType
from sale_portal.config_kpi.models import ExchangePointPos365, ProportionKpiTeam
from sale_portal.config_kpi.serializers import ExchangePointPos365Serializer
from sale_portal.pos365 import Pos365ContractDuration
from sale_portal.utils.permission import get_user_permission_classes


class ExchangePointPos365ViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list ExchangePointPos365 \n
    """
    serializer_class = ExchangePointPos365Serializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = get_user_permission_classes('exchange_point_pos365.list_exchange_point_pos365_config',
                                                             self.request)
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = ExchangePointPos365.objects.all().order_by('id')
        return queryset

    def create(self, request):
        """
            API tạo mới và cập nhật quy đổi point Pos365 \n
            Giá trị type_code lấy từ API /api/pos365s/list-contract-durations
            Request body for this api : Không được bỏ trống \n
                {
                    "exchange_point_pos365s": [
                        {
                            "type_code": 0,
                            "point": 1
                        },
                        {
                            "type_code": 1,
                            "point": 2
                        }
                    ]
                }
        """
        try:
            body = json.loads(request.body)

            exchange_point_pos365s = body.get('exchange_point_pos365s')

            type_code_list = []
            for i in Pos365ContractDuration.CHOICES:
                type_code_list.append(i[0])

            validate_type_code = []

            for item in exchange_point_pos365s:
                if item['type_code'] in validate_type_code:
                    return custom_response(Code.INVALID_BODY, 'type_code is duplicate')
                else:
                    validate_type_code.append(item['type_code'])
                if item['type_code'] not in type_code_list:
                    return custom_response(Code.INVALID_BODY, 'type_code Invalid')
                if not isinstance(item['point'], float):
                    return custom_response(Code.INVALID_BODY, 'point Invalid')

            for update_item in exchange_point_pos365s:
                ExchangePointPos365.objects.get_or_create(type=update_item['type_code'])
                print(update_item['point'])
                ExchangePointPos365.objects.filter(type=update_item['type_code']).update(point=update_item['point'])

            return successful_response('Update or create ExchangePointPos365 success')

        except Exception as e:
            logging.error('Create ExchangePointPos365 exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@login_required
def get_proportion_kpi_team(request):
    """
        API danh sách tỷ trọng KPI Team \n
    """
    data = []
    areas = ProportionKpiTeam.objects.values('area', 'area__name').distinct()

    for item in areas:
        area_item = ProportionKpiTeam.objects.filter(area=item['area']).values('type', 'leader_coefficient').all()
        result = [{
            'type': q['type'],
            'type_name': ProportionKpiTeamType.CHOICES[q['type']][1],
            'leader_coefficient': q['leader_coefficient']
        } for q in area_item]
        data.append({item['area__name']: result})

    return successful_response(data)


@api_view(['GET'])
@login_required
def list_type_proportion_kpi_team(request):
    """
        API get list loại tỷ trọng KPI Team
    """
    data = []
    for item in ProportionKpiTeamType.CHOICES:
        data.append({"type": item[0], "type_name": item[1]})

    return successful_response(data)


@api_view(['PUT'])
@login_required
def update_proportion_kpi_team(request, pk):
    """
        API cập nhật tỷ trọng KPI Team \n
        Request body for this api : Không được bỏ trống \n
            {
                "data": [
                    {
                        "type": 0,
                        "leader_coefficient": 100
                    },
                    {
                        "type": 1,
                        "leader_coefficient": 90
                    },
                    {
                        "type": 2,
                        "leader_coefficient": 80
                    },
                    {
                        "type": 3,
                        "leader_coefficient": 70
                    },
                    {
                        "type": 4,
                        "leader_coefficient": 60
                    },
                    {
                        "type": 5,
                        "leader_coefficient": 50
                    },
                    {
                        "type": 6,
                        "leader_coefficient": 40
                    }
                ]
            }
    """
    try:
        area = Area.objects.filter(pk=pk).first()
        if area is None:
            return custom_response(Code.AREA_NOT_FOUND)

        body = json.loads(request.body)
        data = body.get('data')
        for i in data:
            if not isinstance(i['type'], int) or i['type'] < 0 or i['type'] > 6:
                return custom_response(Code.INVALID_BODY, 'type Invalid')
            if not isinstance(i['leader_coefficient'], int) or i['leader_coefficient'] < 0 or i[
                'leader_coefficient'] > 100:
                return custom_response(Code.INVALID_BODY, 'leader_coefficient Invalid')

        for update_item in data:
            ProportionKpiTeam.objects.get_or_create(
                area=area,
                type=update_item['type']
            )
            ProportionKpiTeam.objects.filter(area=area, type=update_item['type']).update(
                leader_coefficient=update_item['leader_coefficient']
            )

        return successful_response()

    except Exception as e:
        logging.error('Update proportion kpi-team exception: %s', e)
        return custom_response(Code.INTERNAL_SERVER_ERROR)
