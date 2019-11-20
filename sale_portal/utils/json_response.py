import logging

from django.http import JsonResponse

from .error_code_definition import get_error

dev_logger = logging.getLogger('dev')

def success_response(data = None):
    if data is None:
        data = {
            'message': 'Yêu cầu thực hiện thành công'
        }
    if isinstance(data, dict):
        return JsonResponse({
            'status': 'SUCCESS',
            'data': data,
        }, status=200)
    else :
        raise Exception('Response data pass to success_response method  is not a dict, you can also leave it blank')

def error_response(code = None ):
    if code is None:
        code = '000'
    eror_data = get_error(code)
    dev_logger.exception("", extra={"content": eror_data})
    if isinstance(code, str):
        return JsonResponse({
            'status': 'FAILURE',
            'error': eror_data,
        }, status=200)
    else :
        raise Exception('Error code pass to error_response method is not a string, you can also leave it blank')
