from rest_framework.views import exception_handler
from rest_framework.authentication import get_authorization_header
from rest_framework import status
from rest_framework.response import Response
from .models import RequestCount



def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:
        response.data['status'] = response.status_code
        response.data['data'] = {}
    
    
    if response is None:
        return Response(
            data={
                "status":status.HTTP_500_INTERNAL_SERVER_ERROR,
                # "detail":"Internal server error",
                "detail":str(exc),
                "data":{}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response


def Authenticate(self, request):
    auth = get_authorization_header(request).split()
    if not auth or auth[0].lower() != b'token':
        return None
    token = auth[1]
    return token


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        request_count = RequestCount.objects.filter(id=1).first()
        if request_count: 
            request_count.count = request_count.count + 1
            request_count.save()
        else:
            request_count = RequestCount.objects.create(count=1)
        # print('request_count.count' , request_count.count)
        return response
