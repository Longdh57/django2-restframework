from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.postgres.search import SearchVector, SearchQuery

from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import F, Subquery

from sale_portal.shop.models import Shop,vn_unaccent


@api_view(['GET'])
@login_required
def list_shop_for_search(request):
    shop = Shop(
        merchant_id=5,
        staff_id=1,
        name='conditional_escape(name)',
        code=1,
        address='conditional_escape(address)',
        province_id=1,
        district_id=1,
        wards_id=1,
        street='conditional_escape(street)',
        description='conditional_escape(description)',
        created_by=request.user
    )
    shop.save()
    Shop.objects.filter(pk=shop.id).update(
        document=SearchVector(vn_unaccent('address'), weight='B') + SearchVector('code', weight='C') + SearchVector(
            Subquery(Shop.objects.filter(pk=shop.id).values('merchant__merchant_brand')[:1]), weight='C')
    )
    return JsonResponse({
        'status': 'SUCCESS',
        'data': shop.address,
    }, status=200)