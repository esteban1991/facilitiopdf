from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import InvoiceViewSet, SenderProfileView

router = DefaultRouter()
router.register(r"invoices", InvoiceViewSet, basename="invoice")

urlpatterns = [
    path("profile/", SenderProfileView.as_view(), name="sender-profile"),
    path("", include(router.urls)),
]
