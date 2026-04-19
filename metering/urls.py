from django.urls import path, include
from rest_framework.routers import DefaultRouter
from metering.views import MeteringViewSet, BranchMeterViewSet

router = DefaultRouter()
router.register(r'metering', MeteringViewSet, basename = 'metering'),
router.register(r'branchmeter', BranchMeterViewSet, basename = 'branchmeter')

urlpatterns = [
  path('', include(router.urls))
]
