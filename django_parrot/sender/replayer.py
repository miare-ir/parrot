from typing import Iterable

import requests
from django.conf import settings
from django.urls import reverse

from django_parrot.models import RequestLog, ReplayedRequest
from django_parrot.serializers import RequestLogSerializer


def _get_batch_size() -> int:
    if not hasattr(settings, 'PARROT_BATCH_SIZE'):
        return 10
    return settings.PARROT_BATCH_SIZE


def _chunks(some_list, n):
    for i in range(0, len(some_list), n):
        yield some_list[i:i + n]


def _replay_batch(logs: Iterable[RequestLog]):
    body = RequestLogSerializer(logs, many=True).data
    if not hasattr(settings, 'PARROT_LISTENER_HOST'):
        raise KeyError('PARROT_LISTENER_HOST should be set in settings')
    path = reverse('{}:bulk-request-view'.format(settings.PARROT_NAMESPACE))
    url = '{}{}'.format(settings.PARROT_LISTENER_HOST, path)
    response = requests.post(url, json=body)
    response.raise_for_status()
    replayed_requests = [ReplayedRequest(request_id=str(l.id)) for l in logs]
    ReplayedRequest.objects.bulk_create(replayed_requests)


def replay():
    pending = list(RequestLog.objects.filter(replayed=None).order_by('created_at'))
    for chunk in _chunks(pending, _get_batch_size()):
        _replay_batch(chunk)
