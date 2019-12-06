from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models.functions import Lower

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from django.db.models import F, Subquery, Q
from unidecode import unidecode

from sale_portal.shop.models import Shop, vn_unaccent
from sale_portal.shop_cube.models import ShopCube
from sale_portal.utils.geo_utils import findDistance


@api_view(['GET'])
@login_required
def list_shop_for_search(request):
    """
        API để search full text search không dấu  các shop dựa trên địa chỉ, shop_code hoặc merchant brand, param là name
    """
    name = request.GET.get('name', None)
    queryset = Shop.objects.all()
    if name is not None and name != '':
        name_en = unidecode(name).lower()
        search_query = SearchQuery(name_en)
        queryset = queryset.filter(
            Q(document=search_query) \
            | Q(code__icontains=name) | Q(merchant__merchant_brand__icontains=name))

        queryset = queryset.annotate(
            rank=SearchRank(F('document'), search_query)
        ).order_by(
            '-rank'
        )
    data = []
    for shop in queryset[:10]:
        code = shop.code if shop.code is not None else 'N/A'
        address = shop.address if shop.address is not None else 'N/A'
        merchant_brand = shop.merchant.merchant_brand if shop.merchant.merchant_brand is not None else 'N/A'
        data.append({'shop_info': code + ' - ' + address + ' - ' + merchant_brand})
    return JsonResponse({
        'status': 200,
        'data': data
    }, status=200)


@api_view(['GET'])
@login_required
def list_recommend_shops(request, pk):
    '''
    API for get shop number_transaction and nearly shops \n
    :param shop_id
    '''
    current_shop = get_object_or_404(Shop, pk=pk)
    current_shop_shop_cube = ShopCube.objects.filter(shop_id=pk).first()

    if current_shop_shop_cube is not None:
        current_shop_number_of_tran = current_shop_shop_cube.number_of_tran_30d \
            if current_shop_shop_cube.number_of_tran_30d is not None \
               and current_shop_shop_cube.number_of_tran_30d != '' \
            else 'N/A'
    else:
        current_shop_number_of_tran = 'N/A'

    nearly_shops_by_ward = []
    if current_shop.wards != '' and current_shop.wards is not None:
        for shop in Shop.objects.filter(wards=current_shop.wards).exclude(pk=pk):
            code = shop.code if shop.code is not None else 'N/A'
            address = shop.address if shop.address is not None else 'N/A'
            merchant_brand = shop.merchant.merchant_brand if shop.merchant.merchant_brand is not None else 'N/A'
            if shop.latitude is None or shop.longitude is None \
                    or current_shop.latitude is None or current_shop.longitude is None:
                distance = None
            else:
                distance = findDistance(shop.latitude, shop.longitude, current_shop.latitude, current_shop.longitude)
            nearly_shops_by_ward.append({
                'id': shop.id,
                'shop_info': code + ' - ' + address + ' - ' + merchant_brand,
                'address': shop.address,
                'latitude': shop.latitude,
                'longitude': shop.longitude,
                'distance_value': distance.get('value') if distance is not None else None,
                'distance_text': distance.get('text') if distance is not None else None
            })

        nearly_shops_by_latlong = []
        for s_have_distance in nearly_shops_by_ward:
            if s_have_distance.get('distance_value') is not None:
                nearly_shops_by_latlong.append(s_have_distance)
        nearly_shops_by_latlong_sorted = sorted(nearly_shops_by_latlong, key=lambda k: k['distance_value'])
    return JsonResponse({
        'status': 200,
        'data': {
            'address': current_shop.address if current_shop.address != '' and current_shop.address is not None else 'N/A',
            'street': current_shop.street if current_shop.street != '' and current_shop.street is not None else 'N/A',
            'number_of_tran': current_shop_number_of_tran,
            'latitude': current_shop.latitude,
            'longitude': current_shop.longitude,
            'nearly_shops_by_ward': nearly_shops_by_ward[:3],
            'nearly_shops_by_latlong': nearly_shops_by_latlong_sorted[:3]
        }
    }, status=200)
