from sale_portal.qr_status.models import QrStatus


def get_merchant_status_list():
    merchant_status_list = {}
    data = QrStatus.objects.filter(type='MERCHANT').values('code', 'description')
    for item in data:
        merchant_status_list[int(item['code'])] = item['description']
    return merchant_status_list


def get_terminal_status_list():
    terminal_status_list = {}
    data = QrStatus.objects.filter(type='TERMINAL').values('code', 'description')
    for item in data:
        terminal_status_list[int(item['code'])] = item['description']
    return terminal_status_list
