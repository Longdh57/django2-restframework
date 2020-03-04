import json
import pytest

from mixer.backend.django import mixer
from django.test import RequestFactory

from sale_portal.user.models import User
from sale_portal.config_kpi.views import ExchangePointPos365ViewSet


@pytest.fixture
def test_data(db):
    user = mixer.blend(User, username='test_superuser', is_staff=True, is_superuser=True)
    return {'user': user}


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def data(request):
    exchange_point_pos365s = request.param.get('exchange_point_pos365s')
    return {
        "exchange_point_pos365s": exchange_point_pos365s if exchange_point_pos365s is not None else [
            {"type_code": 0, "point": 1.0},
            {"type_code": 1, "point": 2.0},
            {"type_code": 2, "point": 3.0},
            {"type_code": 3, "point": 4.0}
        ]
    }


@pytest.fixture
def status_code(request):
    return request.param


@pytest.fixture
def response_message(request):
    return request.param


@pytest.mark.django_db
@pytest.mark.parametrize(('data', 'status_code', 'response_message'),
                         [
                             ({'exchange_point_pos365s': [
                                 {"type_code": 0, "point": 1.0},
                                 {"type_code": 0, "point": 2.0}
                             ]}, 400, 'type_code is duplicate'),
                             ({'exchange_point_pos365s': [
                                 {"type_code": 0, "point": 1.0},
                                 {"type_code": 10000000, "point": 2.0}
                             ]}, 400, 'type_code Invalid'),
                             ({'exchange_point_pos365s': [
                                 {"type_code": 0, "point": 1.0},
                                 {"type_code": 2, "point": 'abc'}
                             ]}, 400, 'point Invalid')
                         ], indirect=True)
def test_create_data_invalid(test_data, factory, data, status_code, response_message):
    request = factory
    request.user = test_data['user']
    request.method = 'POST'
    request.body = json.dumps(data)

    response = ExchangePointPos365ViewSet().create(request=request)

    assert response.status_code == status_code
    assert response_message in str(json.loads(response.content))
