import uuid
from enum import Enum

from django.db import models


class UUIDPrimaryKey(models.UUIDField):
    def __init__(self, *args, **kwargs):
        kwargs['primary_key'] = True
        kwargs['editable'] = False
        if 'default' in kwargs:
            raise ValueError('default can not be set on UUIDPrimaryKey fields')
        super().__init__(*args, **kwargs)

    def get_pk_value_on_save(self, instance):
        return uuid.uuid4()


class HttpMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    PATCH = 'PATCH'
    PUT = 'PUT'

    @classmethod
    def all(cls):
        return [an_enum for an_enum in cls]

    @classmethod
    def choices(cls):
        return [
            [an_enum.value, an_enum.value] for an_enum in cls.all()
        ]

    def __str__(self):
        return self.value


class RequestLog(models.Model):
    id = UUIDPrimaryKey()
    user_id = models.CharField(max_length=200, null=True, blank=True)
    path = models.CharField(max_length=200)
    body = models.TextField(null=True, blank=True)
    method = models.CharField(max_length=10, choices=HttpMethod.choices())
    replayed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class QueryParams(models.Model):
    id = UUIDPrimaryKey()
    request_log = models.ForeignKey('parrot.RequestLog', on_delete=models.CASCADE)
    key = models.CharField(max_length=200)
    value = models.CharField(max_length=200)
