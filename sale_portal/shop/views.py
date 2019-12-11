from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models.functions import Lower
from django.db import connection

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework import viewsets, mixins
from django.db.models import F, Subquery, Q, Count, FilteredRelation
from unidecode import unidecode
from ..utils.field_formatter import format_string
from ..staff.models import Staff
from ..terminal.models import Terminal

from .serializers import ShopSerializer

from sale_portal.shop.models import Shop, vn_unaccent
from sale_portal.shop_cube.models import ShopCube
from sale_portal.utils.geo_utils import findDistance
from sale_portal.shop import ShopActivateType


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


class ShopViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
        API get list Shop \n
        Parameters for this api : Có thể bỏ trống hoặc không gửi lên
        - code -- text
        - merchant_id -- number
        - team_id -- number
        - staff_id -- number
        - province_id -- number
        - district_id -- number
        - ward_id -- number
        - status -- number in {0, 1, 2, 3, 4} = {Shop không có thông tin đường phố, Shop không có Terminal, Shop có khả năng trùng lặp, Shop đã hủy, Shop chưa được gán Sale}
        - from_date -- dd/mm/yyyy
        - to_date -- dd/mm/yyyy
    """
    serializer_class = ShopSerializer

    def get_queryset(self):

        queryset = Shop.objects.all()

        code = self.request.query_params.get('code', None)
        merchant_id = self.request.query_params.get('merchant_id', None)
        team_id = self.request.query_params.get('team_id', None)
        staff_id = self.request.query_params.get('staff_id', None)
        province_id = self.request.query_params.get('province_id', None)
        district_id = self.request.query_params.get('district_id', None)
        ward_id = self.request.query_params.get('ward_id', None)
        status = self.request.query_params.get('status', None)
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)

        if code is not None and code != '':
            code = format_string(code)
            queryset = queryset.filter(code__icontains=code)

        if merchant_id is not None and merchant_id != '':
            queryset = queryset.filter(merchant_id=merchant_id)

        if team_id is not None and team_id != '':
            staffs = Staff.objects.filter(team=team_id)
            queryset = queryset.filter(staff__in=staffs)

        if staff_id is not None and staff_id != '':
            queryset = queryset.filter(staff=staff_id)

        if province_id is not None and province_id != '':
            queryset = queryset.filter(province=province_id)

        if district_id is not None and district_id != '':
            queryset = queryset.filter(district=district_id)

        if ward_id is not None and ward_id != '':
            queryset = queryset.filter(ward=ward_id)

        if status is not None and status != '':
            if status == '0':
                queryset = queryset.filter(Q(street__isnull=True) | Q(street=''))
            elif status == '1':
                shop_have_terminals = Terminal.objects.filter(shop__isnull=False).values('shop')
                queryset = queryset.exclude(shop_have_terminals)
            elif status == '2':
                dup_ids = []
                with connection.cursor() as cursor:
                    cursor.execute("""
                        select s.id
                        from shop s
                              INNER JOIN (select
                                      merchant_id,
                                      wards_id
                                    from shop
                                    where merchant_id is not null
                                    group by merchant_id, wards_id
                                    having count(merchant_id) > 1) dup
                                ON dup.merchant_id = s.merchant_id and dup.wards_id = s.wards_id
                        where s.activated = 1
                    """)
                    columns = [col[0] for col in cursor.description]
                    data_cursor = [
                        dict(zip(columns, row))
                        for row in cursor.fetchall()
                    ]
                for dup in data_cursor:
                    dup_ids.append(dup['id'])
                queryset = queryset.filter(pk__in=dup_ids)
            elif status == '3':
                queryset = queryset.filter(activated=ShopActivateType.DISABLE)
            elif status == '4':
                queryset = queryset.filter(staff__isnull=True)
            else:
                return ''

        if from_date is not None and from_date != '':
            queryset = queryset.filter(
                created_date__gte=datetime.strptime(from_date, '%d/%m/%Y').strftime('%Y-%m-%d %H:%M:%S'))
        if to_date is not None and to_date != '':
            queryset = queryset.filter(
                created_date__lte=(datetime.strptime(to_date, '%d/%m/%Y').strftime('%Y-%m-%d') + ' 23:59:59'))

        return queryset

    def retrieve(self, request, pk):
        """
            API get detail Merchant
        """
        # return detail(request, pk)
        return "ok"
