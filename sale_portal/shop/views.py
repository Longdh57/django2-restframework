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

    nearly_shops = []
    if current_shop.street != '' and current_shop.street is not None:
        for shop in Shop.objects.annotate(street_lower=Lower('street')).filter(
                street_lower=str(current_shop.street).lower(),
                wards=current_shop.wards
        ).exclude(pk=pk):
            shop_shop_cube = ShopCube.objects.filter(shop_id=pk).first()
            if shop_shop_cube is not None:
                shop_number_of_tran = shop_shop_cube.number_of_tran_30d \
                    if shop_shop_cube.number_of_tran_30d is not None \
                       and shop_shop_cube.number_of_tran_30d != '' \
                    else 'N/A'
            else:
                shop_number_of_tran = 'N/A'
            code = shop.code if shop.code is not None else 'N/A'
            address = shop.address if shop.address is not None else 'N/A'
            merchant_brand = shop.merchant.merchant_brand if shop.merchant.merchant_brand is not None else 'N/A'
            nearly_shops.append({
                'id': shop.id,
                'shop_info': code + ' - ' + address + ' - ' + merchant_brand,
                'address': shop.address,
                'number_of_tran': shop_number_of_tran,
                'latitude': shop.latitude,
                'longitude': shop.longitude
            })
    return JsonResponse({
        'status': 200,
        'data': {
            'address': current_shop.address if current_shop.address != '' and current_shop.address is not None else 'N/A',
            'street': current_shop.street if current_shop.street != '' and current_shop.street is not None else 'N/A',
            'number_of_tran': current_shop_number_of_tran,
            'latitude': current_shop.latitude,
            'longitude': current_shop.longitude,
            'nearly_shops': nearly_shops
        }
    }, status=200)
