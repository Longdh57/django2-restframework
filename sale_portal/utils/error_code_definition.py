error_code_list = {

    # Các lỗi chung
    '000': {'code': '000', 'type': 'COMMON', 'message': 'A few errors have occurred'},
    '001': {'code': '000', 'type': 'COMMON', 'message': 'Some data field or param field is missing'},
    '002': {'code': '000', 'type': 'COMMON', 'message': 'The Request Method is incorrect'},


    # Các lỗi riêng

    # Chức năng sale report
    '100': {'code': '100', 'type': 'SALE_REPORT', 'message': 'The request to the Sale report has failed'},
    '101': {'code': '101', 'type': 'SALE_REPORT', 'message': 'Draft requested revision is overdue'},
}

def get_error(code):
    if code in error_code_list:
        return error_code_list[code]
    else:
        return {'code': '-1', 'type': 'UNIDENTIFIED', 'message': 'Unable to identify the error, an error occurred'},
