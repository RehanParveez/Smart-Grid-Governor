from django.urls import path, include
from rest_framework.routers import DefaultRouter
from economics.views import EconomicsViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'economics', EconomicsViewSet, basename = 'economics')
router.register(r'payment', PaymentViewSet, basename = 'payment')

urlpatterns = [
    path('', include(router.urls)),
]