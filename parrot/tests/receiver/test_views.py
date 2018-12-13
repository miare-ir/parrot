from django.urls import reverse
from drftest import BaseViewTest

from parrot.receiver.views import BulkRequestView


class BulkRequestViewTest(BaseViewTest):
    def _make_url(self, kwargs=None):
        return reverse('parrot:bulk-request-view')

    def _get_view_class(self):
        return BulkRequestView
