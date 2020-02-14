from rest_framework.exceptions import PermissionDenied, AuthenticationFailed, NotAuthenticated
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    message = exc.detail

    if isinstance(exc, NotAuthenticated):
        message = 'Bạn cần phải đăng nhập để thực hiện hành động này.'

    if isinstance(exc, AuthenticationFailed):
        if message == 'Error decoding signature.':
            message = 'Mã xác thực không hợp lệ. Đề nghị đăng nhập lại.'
        if message == 'Signature has expired.':
            message = 'Phiên làm việc đã quá hạn. Bạn cần đăng nhập lại.'

    if isinstance(exc, PermissionDenied):
        message = 'Bạn không có quyền thực hiện hành động này.'

    custom_response_data = {
        'message': message
    }
    response.data = custom_response_data

    return response
