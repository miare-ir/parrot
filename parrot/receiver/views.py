from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class BulkRequestView(APIView):
    def post(self, request: Request) -> Response:
        return Response({'msg': 'Hi'})
