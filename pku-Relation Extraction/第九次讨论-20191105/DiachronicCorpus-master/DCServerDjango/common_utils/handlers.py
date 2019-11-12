from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    def make_detail(errors):
        return ' '.join(['{}字段错误：{}'.format(x, '；'.join(map(str, errors[x]))) for x in errors])
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        if 'detail' not in response.data:
            response.data['detail'] = make_detail(response.data)

    return response
