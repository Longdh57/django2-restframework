from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins

from .models import Staff
from .serializers import StaffSerializer
from ..utils.field_formatter import format_string


class StaffViewSet(mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - staff_code -- text
        - full_name -- text
        - status -- number in {-1,1}
    """
    serializer_class = StaffSerializer

    def get_queryset(self):

        queryset = Staff.objects.all()

        staff_code = self.request.query_params.get('staff_code', None)
        full_name = self.request.query_params.get('full_name', None)
        status = self.request.query_params.get('status', None)

        if staff_code is not None and staff_code != '':
            staff_code = format_string(staff_code)
            queryset = queryset.filter(staff_code__icontains=staff_code)
        if full_name is not None and full_name != '':
            full_name = format_string(full_name)
            queryset = queryset.filter(Q(full_name__icontains=full_name) | Q(email__icontains=full_name))
        if status is not None and status != '':
            queryset = queryset.filter(status=(1 if status == '1' else -1))

        return queryset

    def create(self, request):
        return JsonResponse({
            'data': "post method"
        }, status=200)

    def retrieve(self, request, pk):
        return JsonResponse({
            'data': "get detail method"
        }, status=200)

    def update(self, request, pk):
        return JsonResponse({
            'data': "update method"
        }, status=200)

    def destroy(self, request, pk):
        return JsonResponse({
            'data': "delete method"
        }, status=200)


@api_view(['GET'])
@login_required
def list_staffs(request):
    """
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - email -- text
    """

    queryset = Staff.objects.values('id', 'email', 'full_name')

    email = request.GET.get('email', None)

    if email is not None and email != '':
        queryset = queryset.filter(Q(email__icontains=email) | Q(full_name__icontains=email))

    queryset = queryset.order_by('email')[0:settings.PAGINATE_BY]

    data = [{'id': staff['id'], 'email': staff['full_name'] + ' - ' + staff['email']} for staff in queryset]

    return JsonResponse({
        'data': data
    }, status=200)
