import json
import logging

from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, mixins
from rest_framework.decorators import api_view

from sale_portal.pos365 import Pos365ContractDuration
from sale_portal.config_kpi import ProportionKpiTeamType
from sale_portal.config_kpi.serializers import ExchangePointPos365Serializer
from sale_portal.config_kpi.models import ExchangePointPos365, ProportionKpiTeam
from sale_portal.common.standard_response import successful_response, custom_response, Code


class ExchangePointPos365ViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list ExchangePointPos365 \n
    """
    serializer_class = ExchangePointPos365Serializer

    def get_queryset(self):
        queryset = ExchangePointPos365.objects.all()
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
                if not isinstance(item['point'], int):
                    return custom_response(Code.INVALID_BODY, 'point Invalid')

            for update_item in exchange_point_pos365s:
                ExchangePointPos365.objects.get_or_create(type=update_item['type_code'])
                ExchangePointPos365.objects.filter(type=update_item['type_code']).update(point=update_item['point'])

            return successful_response('Update or create ExchangePointPos365 success')

        except Exception as e:
            logging.error('Create ExchangePointPos365 exception: %s', e)
            return custom_response(Code.INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@login_required
def get_proportion_kpi_team(request):
    """
        API get list proportion kpi team to show \n
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
