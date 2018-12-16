from django.conf.urls import url
from django.test import override_settings
from django.urls import path, reverse
from drftest import BaseViewTest
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from parrot.models import RequestLog
from parrot.sender import recorder


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
    path(
        'dummy/<str:pk>/',
        RecordView.as_view({'delete': 'handle_delete'}),
        name='dummy-with-pk',
    ),
    url(
        r'^dummy/$',
        RecordView.as_view({'put': 'handle_put', 'post': 'handle_post'}),
        name='dummy',
    ),
]


@override_settings(ROOT_URLCONF=__name__)
class ReplayerTest(BaseViewTest):
    def _make_url(self, kwargs=None):
        return reverse('dummy', kwargs=kwargs)

    def _get_view_class(self):
        return RecordView

    def test_default_batch_size(self, *_):
        pass
        # for i in range(15):
        #     RequestLog.objects.create()

    def test_with_multiple_batches(self, *_):
        pass

    def test_with_single_batch(self, *_):
        pass

    def test_avoiding_already_replayed_requests(self, *_):
        pass

    def test_marking_replayed_documents(self, *_):
        pass

    def test_delete_request_with_path_params(self, *_):
        pass

    def test_post_request_with_path_params(self, *_):
        pass

    def test_put_request_with_path_params(self, *_):
        pass
