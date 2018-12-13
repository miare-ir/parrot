import json

from django.test import override_settings
from django.urls import reverse, path
from drftest import BaseViewTest
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from parrot.models import RequestLog, QueryParams
from parrot.sender import recorder


class RecordView(APIView):
    def get(self, request: Request) -> Response:
        recorder.record(request)
        return Response(status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        recorder.record(request)
        return Response(status=status.HTTP_200_OK)


urlpatterns = [
    path('dummy/', RecordView.as_view(), name='dummy')
]


@override_settings(ROOT_URLCONF=__name__)
class RecorderTest(BaseViewTest):
    def _make_url(self, kwargs=None):
        return reverse('dummy', kwargs=kwargs)

    def _get_view_class(self):
        return RecordView

    def test_saves_correct_values_for_log(self, *_):
        response = self._get_for_response(data={'a': 'b'})
        self.assertSuccess(response)
        the_log = RequestLog.objects.first()
        self.assertIsNotNone(the_log)
        self.assertEqual(the_log.path, '/dummy/')

    def test_saves_correct_http_method_for_get(self, *_):
        response = self._get_for_response(data={'a': 'b'})
        self.assertSuccess(response)
        the_log = RequestLog.objects.first()
        self.assertIsNotNone(the_log)
        self.assertEqual(the_log.method, 'GET')

    def test_saves_correct_http_method_for_post(self, *_):
        response = self._post_for_response(data={'a': 'b'})
        self.assertSuccess(response)
        the_log = RequestLog.objects.first()
        self.assertIsNotNone(the_log)
        self.assertEqual(the_log.method, 'POST')

    def test_saves_correct_body_for_get(self, *_):
        response = self._get_for_response(data={'a': 'b'})
        self.assertSuccess(response)
        the_log = RequestLog.objects.first()
        self.assertIsNotNone(the_log)
        self.assertIsNone(response.data)

    def test_saves_correct_query_params(self, *_):
        response = self._get_for_response(data={'a': 'b'})
        self.assertSuccess(response)
        params = QueryParams.objects.first()
        self.assertEqual(params.key, 'a')
        self.assertEqual(params.value, 'b')

    def test_with_multiple_query_params(self, *_):
        response = self._get_for_response(data={'a': 'b', 'c': 'd'})
        self.assertSuccess(response)
        self.assertEqual(2, QueryParams.objects.count())

    def test_saves_body_in_post(self, *_):
        sent_body = {'foo': 'barr'}
        response = self._post_for_response(data=sent_body)
        self.assertSuccess(response)
        the_log = RequestLog.objects.first()
        self.assertIsNotNone(the_log)
        parsed_body = json.loads(the_log.body)
        self.assertEqual(parsed_body, sent_body)
