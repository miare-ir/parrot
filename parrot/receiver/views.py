import json
import logging

from django.urls import resolve
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from parrot.models import RequestLog, HttpMethod, CapturedRequest
from parrot.serializers import RequestLogSerializer


class BulkRequestView(APIView):
    def _build_request(self, log: RequestLog) -> Request:
        factory = APIRequestFactory()
        method = {
            HttpMethod.POST: factory.post,
            HttpMethod.PUT: factory.put,
            HttpMethod.DELETE: factory.delete,
            HttpMethod.PATCH: factory.patch,
        }[log.method]
        return method(log.path, data=log.data)

    def _replay(self, log: RequestLog) -> Response:
        request = self._build_request(log)
        match = resolve(log.path)
        return match.func(request, *match.args, **match.kwargs)

    def post(self, request: Request) -> Response:
        for log_data in request.data:
            try:
                serializer = RequestLogSerializer(data=log_data)
                pk = serializer.validated_data['id']
                if CapturedRequest.objects.filter(request_id=pk).exists():
                    continue
                log = serializer.save()
                captured_request = CapturedRequest.objects.create(request_id=log.id)
                response = self._replay(log)
                captured_request.response_status = response.status_code
                if response.data:
                    captured_request.response_body = json.dumps(response.data)
                captured_request.save()
            except Exception:
                logging.error('Could not handle request on replay')
        return Response(status=status.HTTP_200_OK)
