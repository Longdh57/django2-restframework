from django.db import models


class QrStatus(models.Model):
    code = models.DecimalField(blank=True, null=True, max_digits=38, decimal_places=0)
    description = models.TextField(null=True)
    type = models.TextField(null=True)
    created_date = models.DateTimeField(null=True)
    note = models.TextField(null=True)
    icon = models.TextField(null=True)

    class Meta:
        db_table = 'qr_status'
        default_permissions = ()

    @staticmethod
    def get_merchant_status_list():
        merchant_status_list={}
        data = QrStatus.objects.filter(type='MERCHANT').values('code', 'description')
        for item in data:
            merchant_status_list.pop(item['code'], item['description'])
        return merchant_status_list
