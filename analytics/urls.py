from django.urls import path, include
from rest_framework.routers import DefaultRouter
from analytics.views import CircularDebtViewSet, EfficiencyViewSet, LoadPredictViewSet

router = DefaultRouter()
router.register(r'circulardebt', CircularDebtViewSet, basename = 'circulardebt')
router.register(r'efficiency', EfficiencyViewSet, basename = 'efficiency')
router.register(r'predict', LoadPredictViewSet, basename = 'predict')

urlpatterns = [
    path('', include(router.urls)),
]