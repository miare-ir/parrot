from django.urls import path

from parrot.receiver.views import BulkRequestView

app_name = 'parrot'

urlpatterns = [
    path('parrot/bulk/', BulkRequestView.as_view(), name='bulk-request-view')
]
