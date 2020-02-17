from django.db.models import Q
import logging
from django.utils import formats
from rest_framework import viewsets, mixins
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from rest_framework.decorators import api_view

from sale_portal.utils.permission import get_user_permission_classes
from sale_portal.utils.queryset import get_shops_viewable_queryset
from ..qr_status.views import get_merchant_status_list


from .models import Merchant
from .serializers import MerchantSerializer

from ..utils.field_formatter import format_string
from ..common.standard_response import successful_response, custom_response, Code


class MerchantViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """
        API get list Merchant \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - merchant_code -- text
        - merchant_brand -- text
        - merchant_name -- text
        - status -- number in {-1,1,2,3,4,5,6}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = MerchantSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = get_user_permission_classes('merchant.merchant_list_data', self.request)
        if self.action == 'retrieve':
            permission_classes = get_user_permission_classes('merchant.merchant_detail', self.request)
        return [permission() for permission in permission_classes]

    def get_queryset(self):

        queryset = Merchant.objects.all()

        if self.request.user.is_superuser is False:
            shops = get_shops_viewable_queryset(self.request.user)
            queryset = queryset.filter(pk__in=shops.values('merchant'))

        merchant_code = self.request.query_params.get('merchant_code', None)
        merchant_name = self.request.query_params.get('merchant_name', None)
        merchant_brand = self.request.query_params.get('merchant_brand', None)
        status = self.request.query_params.get('status', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if merchant_code is not None and merchant_code != '':
            merchant_code = format_string(merchant_code)
            queryset = queryset.filter(merchant_code__icontains=merchant_code)
        if merchant_name is not None and merchant_name != '':
            merchant_name = format_string(merchant_name)
            queryset = queryset.filter(merchant_name__icontains=merchant_name)
        if merchant_brand is not None and merchant_brand != '':
            merchant_brand = format_string(merchant_brand)
            queryset = queryset.filter(merchant_brand__icontains=merchant_brand)
        if status is not None and status != '':
            queryset = queryset.filter(status=status)
        if from_date is not None and from_date != '':
            queryset = queryset.filter(
                created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
        if to_date is not None and to_date != '':
            queryset = queryset.filter(
                created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

        return queryset

    def retrieve(self, request, pk):
        """
            API get detail Merchant
        """
        return detail(request, pk)


@api_view(['GET'])
@login_required
@permission_required('merchant.merchant_list_data', raise_exception=True)
def list_merchants(request):
    """
        API get list Merchant to select \n
        Parameters for this api : Có thể bỏ trống hoặc không cần gửi lên
        - code -- text
    """

    queryset = Merchant.objects.values('id', 'merchant_code', 'merchant_name', 'merchant_brand')

    if request.user.is_superuser is False:
        shops = get_shops_viewable_queryset(request.user)
        queryset = queryset.filter(pk__in=shops.values('merchant'))

    code = request.GET.get('code', None)

    if code is not None and code != '':
        queryset = queryset.filter(Q(merchant_code__icontains=code) | Q(merchant_brand__icontains=code))

    queryset = queryset.order_by('merchant_brand')[0:settings.PAGINATE_BY]

    data = [{'id': merchant['id'], 'code': merchant['merchant_code'] + ' - ' + merchant['merchant_brand']} for
            merchant in queryset]

    return successful_response(data)


@login_required
def detail(request, pk):
    # API detail
    try:
        if request.user.is_superuser is False:
            shops = get_shops_viewable_queryset(request.user)
            merchant = Merchant.objects.filter(pk=pk, pk__in=shops.values('merchant')).first()
        else:
            merchant = Merchant.objects.filter(pk=pk).first()
        if merchant is None:
            return custom_response(Code.MERCHANT_NOT_FOUND)
        staff = merchant.get_staff()
        data = {
            'merchant_id': merchant.id,
            'merchant_code': merchant.merchant_code,
            'merchant_brand': merchant.merchant_brand,
            'merchant_name': merchant.merchant_name,
            'address': merchant.address,
            'type': merchant.get_type().full_name if merchant.get_type() else '',
            'staff': {
                'full_name': staff.full_name if staff is not None else '',
                'email': staff.email if staff is not None else ''
            },
            'created_date': formats.date_format(merchant.created_date,
                                                "SHORT_DATETIME_FORMAT") if merchant.created_date else '',
            'status': int(merchant.get_status()) if merchant.get_status() else None,
            'merchant_cube': merchant.get_merchant_cube(),
        }
        return successful_response(data)
    except Exception as e:
        logging.error('Get detail merchant exception: %s', e)
        return custom_response(Code.INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@login_required
def list_status(request):
    """
        API get list status of Merchant
    """
    return successful_response(get_merchant_status_list())
