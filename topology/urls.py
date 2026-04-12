from django.urls import path, include
from rest_framework.routers import DefaultRouter
from topology.views import FeederViewSet, GridViewSet

router = DefaultRouter()
router.register(r'feeder', FeederViewSet, basename = 'feeder'),
router.register(r'grid', GridViewSet, basename = 'grid')

urlpatterns = [
  path('', include(router.urls))
]
