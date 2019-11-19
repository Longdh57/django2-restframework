error_code_list = {
    '000': 'Có một vài lỗi nào đó đã xảy ra',
    '001': 'Request đến server thiếu sót data field hoặc param field nào đó',
    '002': 'Request Method không đúng',
}

def get_error(code):
    if code in error_code_list:
        return {
            'code': code,
            'message': error_code_list[code]
        }
    else:
        raise Exception('code pass to get_error method is not valid')
