import logging
from django.http import JsonResponse
from .code_message import code_message


class Code:
    # Code 2xx
    SUCCESS = "200.000"
    EMPTY_DATA = "200.001"

    CREATE_SUCCESSFULLY = "201.000"

    NO_CHANGE_ANYTHING = "202.000"

    # Code 4xx
    BAD_REQUEST = "400.000"
    INVALID_PARAM = "400.001"
    INVALID_TYPE_PARAM = "400.002"
    MISSING_PARAMS = "400.003"
    INVALID_BODY = "400.004"
    INVALID_TYPE_BODY = "400.005"
    CANNOT_READ_DATA_BODY = "400.006"
    CANNOT_CONVERT_DATA_BODY = "400.007"
    FILE_TYPE_ERROR = "400.008"

    STATUS_NOT_VALID = "400.010"

    AUTHENTICATE_FAILED = "401.000"

    PERMISSION_DENIED = "403.000"

    NOT_FOUND = "404.000"
    STAFF_NOT_FOUND = "404.001"
    TEAM_NOT_FOUND = "404.002"
    MERCHANT_NOT_FOUND = "404.003"
    PROMOTION_NOT_FOUND = "404.004"
    PROMOTION_TITLE_NOT_FOUND = "404.005"
    TERMINAL_NOT_FOUND = "404.006"
    GROUP_NOT_FOUND = "404.007"
    AREA_NOT_FOUND = "404.008"
    USER_NOT_FOUND = "404.009"
    PERMISSION_NOT_FOUND = "404.010"
    SHOP_NOT_FOUND = "404.011"
    ROLE_NOT_FOUND = "404.012"

    # Code 5xx
    INTERNAL_SERVER_ERROR = "500.000"
    DATA_ERROR = "500.001"

    NOT_IMPLEMENTED = "501.000"


def successful_response(data=None):
    return JsonResponse({
        'status': 200,
        'data': data if data is not None else "SUCCESS"
    }, status=200)


def custom_response(code='', message=None):
    return JsonResponse({
        'status': get_status(code),
        'detail_code': code,
        'message': message if message is not None else get_message(code)
    }, status=get_status(code))


def get_status(code):
    if code in code_message:
        try:
            return int(code[:3])
        except Exception as e:
            logging.error(e)
            return 500

    return 500


def get_message(code):
    if code in code_message:
        return code_message[code]
    return "ERROR UNIDENTIFIED"
