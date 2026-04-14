from django.urls import path, include
from rest_framework.routers import DefaultRouter
from topology.views import FeederViewSet, GridViewSet, BranchViewSet

router = DefaultRouter()
router.register(r'feeder', FeederViewSet, basename = 'feeder'),
router.register(r'grid', GridViewSet, basename = 'grid'),
router.register(r'branch', BranchViewSet, basename = 'branch')

urlpatterns = [
  path('', include(router.urls))
]
