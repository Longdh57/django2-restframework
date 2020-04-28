import pytest
from mixer.backend.django import mixer

from sale_portal.shop.models import Shop
from sale_portal.staff_care import StaffCareType
from sale_portal.staff_care.models import StaffCareLog


@pytest.fixture
def shop_id(request):
    return request.param


@pytest.fixture
def staff_id(request):
    return request.param


@pytest.fixture
def response_message(request):
    return request.param


@pytest.mark.django_db
@pytest.mark.parametrize(('shop_id', 'staff_id', 'response_message'),
                         [
                             (44622, 1233, 'Shop already exist a staff')
                         ],
                         indirect=True)
def test_staff_create_invalid(shop_id, staff_id, response_message):
    shop = Shop.objects.get(pk=shop_id)

    with pytest.raises(Exception) as e:
        assert shop.staff_create(staff_id=staff_id, request=None)

    assert response_message in str(e)


@pytest.mark.django_db
@pytest.mark.parametrize(('shop_id', 'staff_id', 'response_message'),
                         [
                             (47407, 1230, 1230)
                         ],
                         indirect=True)
def test_staff_create_success(shop_id, staff_id, response_message):
    shop = Shop.objects.get(pk=shop_id)
    response = shop.staff_create(staff_id=staff_id, request=None)

    staff_care = shop.staff_cares.filter(type=StaffCareType.STAFF_SHOP, staff_id=staff_id).first()
    staff_care_log = StaffCareLog.objects.filter(
        shop=shop,
        staff_id=staff_id,
        type=StaffCareType.STAFF_SHOP,
        is_caring=True
    ).first()

    assert response.id == response_message
    assert staff_care is not None
    assert staff_care_log is not None


@pytest.mark.django_db
@pytest.mark.parametrize(('shop_id', 'staff_id', 'response_message'),
                         [
                             (47407, 1230, 1230)
                         ],
                         indirect=True)
def test_staff_delete_success(shop_id, staff_id, response_message):
    shop = Shop.objects.get(pk=shop_id)
    shop.staff_create(staff_id=staff_id, request=None)

    shop.staff_delete(request=None)

    staff_care_log = StaffCareLog.objects.filter(
        shop=shop,
        staff_id=staff_id,
        type=StaffCareType.STAFF_SHOP,
        is_caring=False
    ).first()

    assert shop.staff is None
    assert staff_care_log is not None
