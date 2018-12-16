import json

from django.conf.urls import url
from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse, path
from drftest import BaseViewTest
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from django_parrot.models import RequestLog
from django_parrot.sender import recorder


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
class RecorderTest(BaseViewTest):
    def setUp(self):
        super().setUp()
        self.user = User.objects.create(username='u1')

    def _make_url(self, kwargs=None):
        return reverse('dummy', kwargs=kwargs)

    def _get_view_class(self):
        return RecordView

    def test_saves_correct_path(self, *_):
        response = self._post_for_response(data={'a': 'b'})
        self.assertSuccess(response)
        the_log = RequestLog.objects.first()
        self.assertIsNotNone(the_log)
        self.assertEqual(the_log.path, '/dummy/')

    def test_saves_correct_http_method(self, *_):
        response = self._post_for_response(data={'a': 'b'})
        self.assertSuccess(response)
        the_log = RequestLog.objects.first()
        self.assertIsNotNone(the_log)
        self.assertEqual(the_log.method, 'POST')

    def test_saves_user_id(self, *_):
        response = self._post_for_response(data={'a': 'b'}, user=self.user)
        self.assertSuccess(response)
        the_log = RequestLog.objects.first()
        self.assertEqual(str(self.user.id), the_log.user_id)

    def test_saves_data(self, *_):
        sent_body = {'foo': 'barr'}
        response = self._post_for_response(data=sent_body)
        self.assertSuccess(response)
        the_log = RequestLog.objects.first()
        self.assertIsNotNone(the_log)
        parsed_body = json.loads(the_log.data)
        self.assertEqual(parsed_body, sent_body)


@override_settings(ROOT_URLCONF=__name__)
class EndpointWithPathParamsTest(BaseViewTest):
    def _make_url(self, kwargs=None):
        return reverse('dummy-with-pk', kwargs=kwargs)

    def _get_view_class(self):
        return RecordView

    def _get_default_url_kwargs(self):
        return {'pk': 1}

    def test_saved_url_for_delete(self):
        response = self._delete_for_response(url_kwargs={'pk': 2})
        self.assertSuccess(response)
        the_log = RequestLog.objects.first()
        self.assertIsNotNone(the_log)
        self.assertEqual(the_log.path, '/dummy/2/')
