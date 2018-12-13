import requests
from django.conf import settings
from django.urls import reverse

from parrot.models import RequestLog
from parrot.serializers import RequestLogSerializer


def _get_batch_size() -> int:
    if not hasattr(settings, 'PARROT_BATCH_SIZE'):
        return 10
    return settings.PARROT_BATCH_SIZE


def replay():
    pending = list(
        RequestLog.objects.order_by('created_at').filter(replayed=False)[:_get_batch_size()]
    )
    body = RequestLogSerializer(pending, many=True).data
    if not hasattr(settings, 'PARROT_LISTENER_HOST'):
        raise KeyError('PARROT_LISTENER_HOST should be set in settings')
    path = reverse('{}:bulk-request-view'.format(settings.PARROT_NAMESPACE))
    url = '{}{}'.format(settings.PARROT_LISTENER_HOST, path)
    response = requests.post(url, body)
    response.raise_for_status()
    ids = [p.id for p in pending]
    RequestLog.objects.filter(id__in=ids).update(replayed=True)
