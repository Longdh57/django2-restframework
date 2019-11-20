from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins

from .models import Team
from .serializers import TeamSerializer
from ..utils.field_formatter import format_string


class TeamViewSet(mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = TeamSerializer

    def get_queryset(self):
        """
            Parameters for this api : Có thể bỏ trống hoặc không gửi lên
            - name -- text
        """

        queryset = Team.objects.all()

        name = self.request.query_params.get('name', None)

        if name is not None and name != '':
            name = format_string(name)
            queryset = queryset.filter(Q(name__icontains=name) | Q(code__icontains=name))

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
def list_teams(request):
    """
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - code -- text
    """

    queryset = Team.objects.values('id', 'code', 'name')

    code = request.GET.get('code', None)

    if code is not None and code != '':
        queryset = queryset.filter(Q(name__icontains=code) | Q(code__icontains=code))

    queryset = queryset.order_by('name')[0:settings.PAGINATE_BY]

    data = [{'id': team['id'], 'name': team['name'] + ' - ' + team['code']} for team in queryset]

    return JsonResponse({
        'data': data
    }, status=200)
