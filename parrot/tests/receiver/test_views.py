import uuid
from traceback import print_exc

from django.contrib.auth.models import User
from django.db import transaction
from django.test import override_settings
from django.urls import reverse, path, include
from drftest import BaseViewTest
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from parrot.models import RequestLog, HttpMethod, CapturedRequest
from parrot.receiver.views import BulkRequestView
from parrot.serializers import RequestLogSerializer


class RecordView(ViewSet):
    def handle_put(self, request: Request) -> Response:
        return Response(status=status.HTTP_200_OK, data={'a': 'b'})

    def handle_delete(self, request: Request, pk) -> Response:
        return Response(status=status.HTTP_200_OK, data={'c': 'd'})

    def handle_post(self, request: Request) -> Response:
        return Response(status=status.HTTP_200_OK, data={'e': 'f'})


urlpatterns = [
    path('prefix/', include('parrot.urls', namespace='parrot')),
    path(
        'dummy/<str:pk>/',
        RecordView.as_view({'delete': 'handle_delete'}),
        name='dummy-with-pk',
    ),
    path(
        'dummy/',
        RecordView.as_view({'put': 'handle_put', 'post': 'handle_post'}),
        name='dummy',
    ),
]


@override_settings(ROOT_URLCONF=__name__)
class BulkRequestViewTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='u1')

    def _make_url(self, kwargs=None):
        return reverse('parrot:bulk-request-view')

    def _get_view_class(self):
        return BulkRequestView

    def test_captured_request_models_are_created(self, *_):
        user_id = uuid.uuid4()
        logs = [
            RequestLog(
                id=uuid.uuid4(),
                user_id=user_id,
                path='/dummy/',
                data='{"a": "b"}',
                method=HttpMethod.POST.value,
            ) for _ in range(15)
        ]
        with transaction.atomic():
            response = self._post_for_response(data=RequestLogSerializer(logs, many=True).data)
        self.assertSuccess(response)
        self.assertEqual(15, CapturedRequest.objects.count())
