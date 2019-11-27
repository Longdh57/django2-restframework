from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import F, Subquery, Q
from unidecode import unidecode

from sale_portal.shop.models import Shop, vn_unaccent


@api_view(['GET'])
@login_required
def list_shop_for_search(request):
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
