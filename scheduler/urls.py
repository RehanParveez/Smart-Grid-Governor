from django.urls import path, include
from rest_framework.routers import DefaultRouter
from scheduler.views import SheddingTargetViewSet, CycleViewSet

router = DefaultRouter()
router.register(r'sheddingtarget', SheddingTargetViewSet, basename = 'sheddingtarget')
router.register(r'cycle', CycleViewSet, basename = 'cycle')

urlpatterns = [
  path('', include(router.urls))
]