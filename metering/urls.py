from django.urls import path, include
from rest_framework.routers import DefaultRouter
from metering.views import MeteringViewSet

router = DefaultRouter()
router.register(r'metering', MeteringViewSet, basename = 'metering')

urlpatterns = [
  path('', include(router.urls))
]
