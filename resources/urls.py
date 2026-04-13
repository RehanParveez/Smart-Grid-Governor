from django.urls import path, include
from rest_framework.routers import DefaultRouter
from resources.views import GenerationUnitViewSet

router = DefaultRouter()
router.register(r'generationunit', GenerationUnitViewSet, basename = 'generationunit')

urlpatterns = [
  path('', include(router.urls))
]
