# import json
# import pytest
#
# from django.http import HttpRequest
# from mixer.backend.django import mixer
# from django.test import RequestFactory
#
# from sale_portal.user.models import User
# from sale_portal.terminal.models import Terminal
#
#
# @pytest.fixture
# def user(db):
#     return mixer.blend(User, username='test_superuser', is_staff=True, is_superuser=True)
#
#
# @pytest.fixture
# def data(request):
#     terminal_id = request.param.get('terminal_id')
#     if terminal_id is not None:
#         terminal = Terminal.objects.get(pk=terminal_id)
#     else:
#         terminal = Terminal.objects.filter(shop_id__isnull=True, status=1, ph__gt=50000).first()
#     street = request.param.get('street')
#     return {
#         'terminal': terminal,
#         'street': street if street is not None else ''
#     }
#
#
# @pytest.fixture
# def factory():
#     return HttpRequest()
#
#
# @pytest.fixture
# def status_code(request):
#     return request.param
#
#
# @pytest.fixture
# def response_message(request):
#     return request.param
#
#
# @pytest.mark.django_db
# def test_create_shop_from_terminal_invalid(user, factory, data, status_code, response_message):
#     request = factory
#     request.user = user
#     request.method = 'OTHER'
#     request.terminal = terminal
#     request.address = terminal.business_address
#     request.street = ''
#
#     response = TeamViewSet().create(request=request)
#
#     assert response.status_code == status_code
#     assert response_message in str(json.loads(response.content))
