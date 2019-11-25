import logging
from django.db.models import Q
from datetime import datetime

from django.template.response import TemplateResponse
from django.utils import formats
from django.http import JsonResponse

from django.conf import settings
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required

from rest_framework import viewsets, mixins
from .serializers import TerminalSerializer
from .models import Terminal
from ..utils.field_formatter import format_string
from ..shop.models import Shop
from ..staff.models import Staff
from ..qr_status.views import get_terminal_status_list


def index(request):
    return TemplateResponse(request, 'terminal/index.html')


class TerminalViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
        API get list Terminal \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - terminal_id -- text
        - terminal_name -- text
        - merchant_id -- number
        - staff_id -- number
        - team_id -- number
        - province_code -- text
        - district_code -- text
        - ward_code -- text
        - status -- number in {-1,1,2,3,4,5,6}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = TerminalSerializer

    def get_queryset(self):

        queryset = Terminal.objects.all()

        terminal_id = self.request.query_params.get('terminal_id', None)
        terminal_name = self.request.query_params.get('terminal_name', None)
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
            queryset = queryset.filter(terminal_id__icontains=terminal_id)

        if terminal_name is not None and terminal_name != '':
            terminal_name = format_string(terminal_name)
            queryset = queryset.filter(terminal_name__icontains=terminal_name)

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

    def retrieve(self, request, pk):
        """
            API get detail Terminal
        """
        return detail(request, pk)

    def update(self, request, pk):
        """
            API update Terminal
        """
        return JsonResponse({
            'status': 200,
            'data': "update method"
        }, status=200)


@api_view(['GET'])
@login_required
def list_terminals(request):

    """
        API get list Terminal to select \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
        - merchant_id -- number
    """

    queryset = Terminal.objects.values('id', 'terminal_id', 'terminal_name')

    name = request.GET.get('name', None)
    merchant_id = request.GET.get('merchant_id', None)

    if name is not None and name != '':
        queryset = queryset.filter(Q(terminal_id__icontains=name) | Q(terminal_name__icontains=name))
    if merchant_id is not None and merchant_id != '':
        queryset = queryset.filter(merchant_id=merchant_id)

    queryset = queryset.order_by('terminal_name')[0:settings.PAGINATE_BY]

    data = [{'id': terminal['id'], 'name': terminal['terminal_id'] + ' - ' + terminal['terminal_name']} for
            terminal in queryset]

    return JsonResponse({
        'status': 200,
        'data': data
    }, status=200)


@login_required
def detail(request, pk):
    try:
        terminal = Terminal.objects.filter(pk=pk).first()
        if terminal is None:
            return JsonResponse({
                'status': 404,
                'message': 'Terminal not found'
            }, status=404)

        merchant = terminal.merchant
        shop = terminal.shop
        staff = shop.staff if shop else None
        team = staff.team if staff else None
        staff_chain = shop.staff_of_chain if shop else None
        team_chain = staff_chain.team if staff_chain else None

        data = {
            'terminal_id': terminal.terminal_id,
            'terminal_name': terminal.terminal_name,
            'terminal_address': terminal.terminal_address,
            'province_name': terminal.get_province().province_name if terminal.get_province() else '',
            'district_name': terminal.get_district().district_name if terminal.get_district() else '',
            'wards_name': terminal.get_wards().wards_name if terminal.get_wards() else '',
            'business_address': terminal.business_address,
            'merchant': {
                'id': merchant.id if merchant else '',
                'name': merchant.merchant_name if merchant else '',
                'code': merchant.merchant_code if merchant else '',
                'brand': merchant.merchant_brand if merchant else '',
            },
            'shop': {
                'id': shop.id if shop else '',
                'name': shop.name if shop else '',
                'code': shop.code if shop else '',
                'address': shop.address if shop else '',
                'street': shop.street if shop else '',
                'take_care_status': shop.take_care_status if shop else '',
                'activated': shop.activated if shop else '',
                'province_name': shop.province.province_name if (shop and shop.province) else '',
                'district_name': shop.district.district_name if (shop and shop.district) else '',
                'wards_name': shop.wards.wards_name if (shop and shop.wards) else '',
                'staff': {
                    'full_name': staff.full_name if staff else '',
                    'email': staff.email if staff else ''
                },
                'team': {
                    'code': team.code if team else '',
                    'name': team.name if team else ''
                },
                'staff_chain': {
                    'full_name': staff_chain.full_name if staff_chain else '',
                    'email': staff_chain.email if staff_chain else ''
                },
                'team_chain': {
                    'code': team_chain.code if team_chain else '',
                    'name': team_chain.name if team_chain else ''
                }
            },
            'created_date': formats.date_format(terminal.created_date,
                                                "SHORT_DATETIME_FORMAT") if terminal.created_date else '',
            'status': int(terminal.get_status()) if terminal.get_status() else None,
        }
        return JsonResponse({
            'status': 200,
            'data': data
        }, status=200)
    except Exception as e:
        logging.error('Get detail terminal exception: %s', e)
        return JsonResponse({
            'status': 500,
            'message': 'Internal sever error'
        }, status=500)


@api_view(['GET'])
@login_required
def list_status(request):
    """
        API get list status of Terminal
    """
    return JsonResponse({
        'status': 200,
        'data': get_terminal_status_list()
    }, status=200)
