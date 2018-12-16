from rest_framework import serializers

from parrot.models import RequestLog


class RequestLogSerializer(serializers.ModelSerializer):
    id = serializers.CharField()

    class Meta:
        model = RequestLog
        fields = '__all__'
