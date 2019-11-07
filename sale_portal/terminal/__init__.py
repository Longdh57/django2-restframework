class TerminalLogType:
    CREATE_NEW = 0
    DELETED = 1
    CHANGE_STATUS = 2
    CHANGE_TERMINAL_ADDRESS = 3
    CHANGE_TERMINAL_NAME = 4
    CHANGE_REGISTER_QR = 5
    CHANGE_REGISTER_VNPAYMENT = 6
    CHANGE_WARDS_CODE = 7
    CHANGE_BUSINESS_ADDRESS = 8
    CHANGE_SHOP = 9

    CHOICES = [
        (CREATE_NEW, 'New row in qr_terminal table'),
        (DELETED, 'Deleted in qr_terminal table'),
        (CHANGE_STATUS, 'Change in field status'),
        (CHANGE_TERMINAL_ADDRESS, 'Change in field terminal_address'),
        (CHANGE_TERMINAL_NAME, 'Change in field terminal_name'),
        (CHANGE_REGISTER_QR, 'Change in field register_qr'),
        (CHANGE_REGISTER_VNPAYMENT, 'Change in field register_vnpayment'),
        (CHANGE_WARDS_CODE, 'Change in field wards_code'),
        (CHANGE_BUSINESS_ADDRESS, 'Change in field business_address'),
        (CHANGE_SHOP, 'Change in field shop'),
    ]