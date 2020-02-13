from rest_framework.exceptions import PermissionDenied, AuthenticationFailed, NotAuthenticated
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, NotAuthenticated):
        custom_response_data = {
            'message': 'Bạn cần phải đăng nhập để thực hiện hành động này.'    # custom exception message
        }
        response.data = custom_response_data    # set the custom response data on response object

    # if isinstance(exc, AuthenticationFailed):
    #     custom_response_data = {
    #         'message': 'Sai tài khoản đăng nhập. Đăng nhập thất bại!'
    #     }
    #     response.data = custom_response_data

    if isinstance(exc, PermissionDenied):
        custom_response_data = {
            'message': 'Bạn không có quyền thực hiện hành động này.'
        }
        response.data = custom_response_data

    return response
