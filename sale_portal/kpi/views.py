from datetime import datetime

import dateutil.relativedelta
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required, permission_required

from sale_portal.common.standard_response import successful_response
from sale_portal.config_kpi.models import ExchangePointPos365
from sale_portal.kpi.models import Kpi
from sale_portal.pos365.models import Pos365
from sale_portal.shop.models import Shop
from sale_portal.shop_cube.models import ShopCube

COEFFICIENT_POINT_SHOP_S10 = 8


@api_view(['GET'])
@login_required
def get_data_kpi_yourself(request):

    data = {
        'target_kpi': 0,
        'count_shop_new': 0,
        'count_shop_s10': 0,
        'point_shop_s10': 0,
        'count_contract': 0,
        'point_contract': 0,
        'point_promotion_form': 0,
        'point_other': 0
    }

    kpi = Kpi.objects.filter(email=request.user.email, month=datetime.now().month, year=datetime.now().year).first()
    if kpi is not None:
        data['target_kpi'] = kpi.kpi_target
        data['point_promotion_form'] = kpi.kpi_point_lcc
        data['point_other'] = kpi.kpi_point_other

    contract_pos365s = Pos365.objects.filter(staff__email=request.user.email).all()
    data['count_contract'] = contract_pos365s.count()
    if data['count_contract'] != 0:
        exchange_points = {}
        for exchange_point_pos365 in ExchangePointPos365.objects.all():
            exchange_points[exchange_point_pos365.type] = exchange_point_pos365.point
        for contract in contract_pos365s:
            if exchange_points[contract.contract_duration] is not None:
                data['point_contract'] = data['point_contract'] + exchange_points[
                    contract.contract_duration] * contract.contract_coefficient / 100

    shop_list = []
    for shop in Shop.objects.filter(created_date__gte=get_day_22_previous_month()).all().values('id'):
        shop_list.append(shop['id'])
    shop_news = ShopCube.objects.filter(shop_id__in=shop_list, number_of_tran_last_m__lt=10).all()
    data['count_shop_new'] = shop_news.count()
    for shop_new in shop_news:
        if (shop_new.number_of_tran_acm + shop_new.number_of_tran_last_m) >= 10:
            data['count_shop_s10'] += 1
    data['point_shop_s10'] = data['count_shop_s10'] * COEFFICIENT_POINT_SHOP_S10
    return successful_response(data)


def get_day_22_previous_month():
    return (datetime.now() + dateutil.relativedelta.relativedelta(months=-1)).replace(day=22)
