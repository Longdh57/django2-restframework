from django.db.models import Q
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.utils import formats
from rest_framework import viewsets, mixins
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view


from .models import Merchant
from .serializers import MerchantSerializer

from ..utils.field_formatter import format_string


def index(request):
    return TemplateResponse(request, 'merchant/index.html')


class MerchantViewSet(mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = MerchantSerializer

    def get_queryset(self):

        queryset = Merchant.objects.all()

        merchant_code = self.request.query_params.get('merchant_code', None)
        staff_id = self.request.query_params.get('staff_id', None)
        status = self.request.query_params.get('status', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if merchant_code is not None and merchant_code != '':
            merchant_code = format_string(merchant_code)
            queryset = queryset.filter(
                Q(merchant_code__icontains=merchant_code) | Q(merchant_name__icontains=merchant_code) | Q(
                    merchant_brand__icontains=merchant_code))
        if staff_id is not None and staff_id != '':
            queryset = queryset.filter(staff=staff_id)
        if status is not None and status != '':
            queryset = queryset.filter(status=status)
        if from_date is not None and from_date != '':
            queryset = queryset.filter(
                created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
        if to_date is not None and to_date != '':
            queryset = queryset.filter(
                created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

        return queryset


def show(request, pk):
    ctx = {
        'pk': pk,
    }
    return TemplateResponse(request, 'merchant/show.html', ctx)


@api_view(['GET'])
@login_required
def list_merchants(request):

    queryset = Merchant.objects.values('id', 'merchant_code', 'merchant_name', 'merchant_brand')

    code = request.GET.get('code', None)

    if code is not None and code != '':
        queryset = queryset.filter(Q(merchant_code__icontains=code) | Q(merchant_brand__icontains=code))

    queryset = queryset.order_by('merchant_brand')[0:settings.PAGINATE_BY]

    data = [{'id': merchant['id'], 'code': merchant['merchant_code'] + ' - ' + merchant['merchant_brand']} for
            merchant in queryset]

    return JsonResponse({
        'data': data
    }, status=200)


@api_view(['GET'])
@login_required
def detail(request, pk):
    # API detail
    merchant = get_object_or_404(Merchant, pk=pk)
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
        'status': merchant.get_status(),
        'merchant_cube': merchant.get_merchant_cube(),
    }
    return JsonResponse({
        'data': data
    }, status=200)


def create(request):
    # Trả về view tạo mới, ví dụ TemplateResponse(request, 'merchant/create.html')
    pass


def store(request):
    # API tạo mới
    pass


def edit(request, pk):
    # Trả về view edit, ví dụ TemplateResponse(request, 'merchant/edit.html')
    pass


def update(request, pk):
    # API cập nhật
    pass


def delete(request, pk):
    # API xóa
    pass
