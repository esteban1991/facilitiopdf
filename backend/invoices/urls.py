from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ClientViewSet, InvoiceViewSet, SenderProfileView, stats

router = DefaultRouter()
router.register(r"clients", ClientViewSet, basename="client")
router.register(r"invoices", InvoiceViewSet, basename="invoice")

urlpatterns = [
    path("profile/", SenderProfileView.as_view(), name="sender-profile"),
    path("stats/", stats, name="stats"),
    path("", include(router.urls)),
]
