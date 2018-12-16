import uuid
from unittest import mock

import requests
from django.test import override_settings
from django.urls import path, reverse, include
from drftest import BaseViewTest
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from django_parrot.models import RequestLog, HttpMethod, ReplayedRequest
from django_parrot.sender import recorder, replayer


class RecordView(ViewSet):
    def handle_put(self, request: Request) -> Response:
        recorder.record(request)
        return Response(status=status.HTTP_200_OK)

    def handle_delete(self, request: Request, pk) -> Response:
        recorder.record(request)
        return Response(status=status.HTTP_200_OK)

    def handle_post(self, request: Request) -> Response:
        recorder.record(request)
        return Response(status=status.HTTP_200_OK)


urlpatterns = [
    path('prefix/', include('django_parrot.urls', namespace='parrot')),
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
@mock.patch.object(requests, 'post')
class ReplayerTest(BaseViewTest):
    def _make_url(self, kwargs=None):
        return reverse('dummy', kwargs=kwargs)

    def _get_view_class(self):
        return RecordView

    def test_serializing_ids(self, mocked_post, *_):
        user_id = uuid.uuid4()
        for i in range(15):
            RequestLog.objects.create(
                user_id=user_id,
                path='/dummy/',
                data={'a': 'b'},
                method=HttpMethod.POST.value,
            )
        replayer.replay()
        self.assertEqual(mocked_post.call_count, 2)
        args, kwargs = mocked_post.call_args_list[0]
        self.assertEqual(len(kwargs['json']), 10)
        for log_data in kwargs['json']:
            self.assertIsNotNone(log_data.get('id'))

    def test_default_batch_size(self, mocked_post, *_):
        user_id = uuid.uuid4()
        for i in range(15):
            RequestLog.objects.create(
                user_id=user_id,
                path='/dummy/',
                data={'a': 'b'},
                method=HttpMethod.POST.value,
            )
        replayer.replay()
        self.assertEqual(mocked_post.call_count, 2)
        args, kwargs = mocked_post.call_args_list[0]
        self.assertEqual(len(kwargs['json']), 10)
        args, kwargs = mocked_post.call_args_list[1]
        self.assertEqual(len(kwargs['json']), 5)

    @override_settings(PARROT_BATCH_SIZE=20)
    def test_with_batch_size_in_settings(self, mocked_post, *_):
        user_id = uuid.uuid4()
        for i in range(15):
            RequestLog.objects.create(
                user_id=user_id,
                path='/dummy/',
                data={'a': 'b'},
                method=HttpMethod.POST.value,
            )
        replayer.replay()
        self.assertEqual(mocked_post.call_count, 1)
        args, kwargs = mocked_post.call_args_list[0]
        self.assertEqual(len(kwargs['json']), 15)

    @override_settings(PARROT_BATCH_SIZE=20)
    def test_avoiding_already_replayed_requests(self, mocked_post, *_):
        user_id = uuid.uuid4()
        for i in range(15):
            RequestLog.objects.create(
                user_id=user_id,
                path='/dummy/',
                data={'a': 'b'},
                method=HttpMethod.POST.value,
            )
        replayer.replay()
        self.assertEqual(mocked_post.call_count, 1)
        args, kwargs = mocked_post.call_args_list[0]
        self.assertEqual(len(kwargs['json']), 15)
        mocked_post.reset_mock()
        self.assertEqual(
            0, mocked_post.call_count,
            'Should not do anything when all requests are already replayed')

    def test_marking_replayed_documents(self, *_):
        user_id = uuid.uuid4()
        logs = [
            RequestLog.objects.create(
                user_id=user_id,
                path='/dummy/',
                data={'a': 'b'},
                method=HttpMethod.POST.value,
            ) for _ in range(15)
        ]
        replayer.replay()
        for log in logs:
            self.assertTrue(ReplayedRequest.objects.filter(request=log).exists())

    def test_url_of_bulk_request(self, mocked_post, *_):
        user_id = uuid.uuid4()
        for i in range(1):
            RequestLog.objects.create(
                user_id=user_id,
                path='/dummy/',
                data={'a': 'b'},
                method=HttpMethod.POST.value,
            )
        replayer.replay()
        self.assertEqual(mocked_post.call_count, 1)
        args, kwargs = mocked_post.call_args_list[0]
        self.assertEqual(args[0], 'http://example.com/prefix/parrot/bulk/')
