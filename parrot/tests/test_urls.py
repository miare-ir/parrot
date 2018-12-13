from django.conf.urls import url
from django.urls import include

urlpatterns = [
    url(r'^', include('parrot.urls', namespace='parrot')),
]
