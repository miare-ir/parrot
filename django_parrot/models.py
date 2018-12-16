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


class CharFieldEnum(Enum):
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


class HttpMethod(CharFieldEnum):
    POST = 'POST'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    PUT = 'PUT'


class RequestLog(models.Model):
    id = UUIDPrimaryKey()
    user_id = models.CharField(max_length=200, null=True, blank=True)
    path = models.CharField(max_length=200)
    data = models.TextField(null=True, blank=True)
    method = models.CharField(max_length=10, choices=HttpMethod.choices())
    created_at = models.DateTimeField(auto_now_add=True)


class ReplayedRequest(models.Model):
    id = UUIDPrimaryKey()
    request = models.OneToOneField(
        'django_parrot.RequestLog', on_delete=models.CASCADE, related_name='replayed')
    created_at = models.DateTimeField(auto_now_add=True)


class CapturedRequest(models.Model):
    request_id = models.UUIDField()
    response_status = models.IntegerField(null=True, blank=True)
    response_body = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
