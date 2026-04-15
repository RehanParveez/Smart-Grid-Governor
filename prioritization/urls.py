from django.urls import path, include
from rest_framework.routers import DefaultRouter
from prioritization.views import PrioritizationViewSet

router = DefaultRouter()
router.register(r'priority', PrioritizationViewSet, basename = 'priority')

urlpatterns = [
  path('', include(router.urls))
]