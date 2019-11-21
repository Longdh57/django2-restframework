import json
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
    """
        API get list Team \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - name -- text
    """
    serializer_class = TeamSerializer

    def get_queryset(self):

        queryset = Team.objects.all()

        name = self.request.query_params.get('name', None)

        if name is not None and name != '':
            name = format_string(name)
            queryset = queryset.filter(Q(name__icontains=name) | Q(code__icontains=name))

        return queryset

    def create(self, request):
        """
            API create team
        """
        body = json.loads(request.body)
        name = code = description = None
        if 'name' in body:
            name = body['name']
        if 'code' in body:
            code = body['code']
        if 'description' in body:
            description = body['description']

        if name is None or name == '' or code is None or code == '':
            return JsonResponse({
                'message': 'Invalid body (name or code invalid)'
            }, status=400)

        name = format_string(name)
        code = format_string(code)

        team = Team.objects.filter(Q(name=name) | Q(code=code)).first()

        if team is not None:
            return JsonResponse({
                'message': 'name or code be used by other Team'
            }, status=400)

        team = Team(
            code=code,
            name=name,
            description=description
        )
        team.save()

        return JsonResponse({
            'data': team.id
        }, status=201)

    def retrieve(self, request, pk):
        """
            API get detail Team
        """
        return JsonResponse({
            'data': "get detail method"
        }, status=200)

    def update(self, request, pk):
        """
            API update Team
        """
        return JsonResponse({
            'data': "update method"
        }, status=200)

    def destroy(self, request, pk):
        """
            API delete Team
        """
        return JsonResponse({
            'data': "delete method"
        }, status=200)


@api_view(['GET'])
@login_required
def list_teams(request):
    """
        API get list Team to select \n
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
