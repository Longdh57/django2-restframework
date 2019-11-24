import json

from django.test import TestCase
from sale_portal.user.models import User
from rest_framework.test import APIClient

from .models import SaleReport


class SaleReportTestCase(TestCase):
    def setUp(self):
        print('set up')

    def test_sale_report_for_open_new(self):
        client = APIClient()
        # user = User.objects.get(username='dev')
        client.force_authenticate(user=None)
        response = client.post('/api/sale-report-form/store/',
                               json.dumps({
                                   "purpose": "0",
                                   "longitude": "100.15526",
                                   "latitude": "101.5656",
                                   "is_draft": "true",
                                   "current_draft_id": "10",
                                   "new_merchant_name": "test new_merchant_name",
                                   "new_merchant_brand": "merchant brand",
                                   "new_address": "test new_address",
                                   "new_customer_name": "test dnew customer name",
                                   "new_phone": "+8412345678",
                                   "new_result": "0",
                                   "new_note": "note",
                                   "new_using_application": "iPos",
                                   "shop_id": "1"
                                }),
                               content_type='application/json')
        self.assertEqual(response.status_code, 200)