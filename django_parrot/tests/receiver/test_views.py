import datetime
import uuid
from unittest import mock
from unittest.mock import ANY

from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse, path, include
from django.utils import timezone
from drftest import BaseViewTest
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from django_parrot.models import RequestLog, HttpMethod, CapturedRequest
from django_parrot.receiver.views import BulkRequestView
from django_parrot.serializers import RequestLogSerializer


class RecordView(ViewSet):
    def handle_put(self, request: Request) -> Response:
        return Response(status=status.HTTP_200_OK, data={'a': 'b'})

    def handle_delete(self, request: Request, pk) -> Response:
        return Response(status=status.HTTP_200_OK, data={'c': 'd'})

    def handle_post(self, request: Request) -> Response:
        return Response(status=status.HTTP_200_OK, data={'e': 'f'})


urlpatterns = [
    path('prefix/', include('django_parrot.urls', namespace='parrot')),
    path(
        'dummy/<int:pk>/',
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
            ) for _ in range(3)
        ]
        response = self._post_for_response(data=RequestLogSerializer(logs, many=True).data)
        self.assertSuccess(response)
        self.assertEqual(3, CapturedRequest.objects.count())

    @mock.patch.object(timezone, 'now', return_value=datetime.datetime.utcnow())
    def test_response_is_captured_correctly_for_post(self, mocked_now, *_):
        user_id = uuid.uuid4()
        logs = [
            RequestLog(
                id=uuid.uuid4(),
                user_id=user_id,
                path='/dummy/',
                data='{"a": "b"}',
                method=HttpMethod.POST.value,
            ),
        ]
        response = self._post_for_response(data=RequestLogSerializer(logs, many=True).data)
        self.assertSuccess(response)
        captured = CapturedRequest.objects.first()
        self.assertIsNotNone(captured)
        self.assertEqual(captured.response_status, status.HTTP_200_OK)
        self.assertEqual(captured.response_body, '{"e": "f"}')
        self.assertEqual(mocked_now.return_value, captured.created_at)

    def test_response_is_captured_correctly_for_delete(self, *_):
        user_id = uuid.uuid4()
        logs = [
            RequestLog(
                id=uuid.uuid4(),
                user_id=user_id,
                path='/dummy/4/',
                method=HttpMethod.DELETE.value,
            ),
        ]
        response = self._post_for_response(
            data=RequestLogSerializer(logs, many=True).data
        )
        self.assertSuccess(response)
        captured = CapturedRequest.objects.first()
        self.assertIsNotNone(captured)
        self.assertEqual(captured.response_status, status.HTTP_200_OK)
        self.assertEqual(captured.response_body, '{"c": "d"}')

    @mock.patch.object(RecordView, 'handle_delete', return_value=Response())
    def test_correct_path_params_are_passed_to_view(self, mocked_delete, *_):
        user_id = uuid.uuid4()
        logs = [
            RequestLog(
                id=uuid.uuid4(),
                user_id=user_id,
                path='/dummy/4/',
                method=HttpMethod.DELETE.value,
            ),
        ]
        response = self._post_for_response(
            data=RequestLogSerializer(logs, many=True).data
        )
        self.assertSuccess(response)
        captured = CapturedRequest.objects.first()
        self.assertIsNotNone(captured)
        mocked_delete.assert_called_with(ANY, pk=4)
