import json
from typing import Optional

from rest_framework.request import Request

from django_parrot.models import RequestLog


def _get_user_id(request: Request) -> Optional[str]:
    if request.user.is_anonymous:
        return None
    return request.user.id


def _get_path(request: Request) -> str:
    path_with_query = request.get_full_path()
    if '?' not in path_with_query:
        return path_with_query
    query_start = path_with_query.index('?')
    return path_with_query[:query_start]


def _get_data(request: Request) -> Optional[str]:
    body = request.data
    if not body:
        return None
    try:
        return json.dumps(request.data)
    except Exception as e:
        raise ValueError('request body is not json-serializable.') from e


def record(request: Request):
    the_log = RequestLog.objects.create(
        user_id=_get_user_id(request),
        path=_get_path(request),
        data=_get_data(request),
        method=request.method,
    )
    return the_log
