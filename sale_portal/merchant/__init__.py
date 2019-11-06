class MerchantLogType:
    CREATE_NEW = 0
    DELETED = 1
    CHANGE_STATUS = 2
    CHANGE_MERCHANT_ADDRESS = 3
    CHANGE_MERCHANT_NAME = 4
    CHANGE_MERCHANT_CODE = 5
    CHANGE_MERCHANT_BRAND = 6
    CHANGE_MERCHANT_TYPE = 7
    CHANGE_STAFF = 8

    CHOICES = [
        (CREATE_NEW, 'New row in qr_merchant table'),
        (DELETED, 'Deleted in qr_merchant table'),
        (CHANGE_STATUS, 'Change in field status'),
        (CHANGE_MERCHANT_ADDRESS, 'Change in field merchant_address'),
        (CHANGE_MERCHANT_NAME, 'Change in field merchant_name'),
        (CHANGE_MERCHANT_CODE, 'Change in field merchant_code'),
        (CHANGE_MERCHANT_BRAND, 'Change in field merchant_brand'),
        (CHANGE_MERCHANT_TYPE, 'Change in field merchant_type_id'),
        (CHANGE_STAFF, 'Change in field staff'),
    ]