from django.db.models import Q
from django.http import JsonResponse
from django.template.response import TemplateResponse
from rest_framework import viewsets
from datetime import datetime

from .models import Merchant
from .serializers import MerchantSerializer

from ..utils.field_formatter import format_string


def index(request):
    return TemplateResponse(request, 'merchant/index.html')


class MerchantViewSet(viewsets.ModelViewSet):
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
    # Trả về view, ví dụ TemplateResponse(request, 'merchant/show.html')
    pass


def detail(request, pk):
    # API detail
    return JsonResponse({
        'data': 'Hello Binh',
        'pk': pk
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
