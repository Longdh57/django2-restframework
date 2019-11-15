from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from rest_framework.decorators import api_view

from ..staff.models import Staff


@api_view(['GET'])
@login_required
def list_staffs(request):

    queryset = Staff.objects.values('id', 'email', 'full_name')

    email = request.GET.get('email', None)

    if email is not None and email != '':
        queryset = queryset.filter(Q(email__icontains=email) | Q(full_name__icontains=email))

    queryset = queryset.order_by('email')[0:settings.PAGINATE_BY]

    data = [{'id': staff['id'], 'email': staff['full_name'] + ' - ' + staff['email']} for staff in queryset]

    return JsonResponse({
        'data': data
    }, status=200)
