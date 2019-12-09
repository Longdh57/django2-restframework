import logging
import socket
import time

request_logger = logging.getLogger('request')


def RequestLogMiddleware(get_response):
    log_data= {}

    def middleware(request):
        try:
            request.start_time = time.time()

            response = get_response(request)

            log_data['remote_address'] = request.META['REMOTE_ADDR']
            log_data['agent'] = request.META['HTTP_USER_AGENT']
            log_data['server_hostname'] = socket.gethostname()
            log_data['request_method'] = request.method
            log_data['request_path'] = request.get_full_path()
            log_data['run_time'] = time.time() - request.start_time
            log_data['status_code'] = response.status_code
            request_logger.debug(msg='', extra=log_data)
            return response
        except Exception as e:
            request_logger.exception(msg='', extra=log_data)
            return get_response(request)
    return middleware
