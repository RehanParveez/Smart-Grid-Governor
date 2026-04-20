from django.urls import path, include
from rest_framework.routers import DefaultRouter
from resources.views import GenerationUnitViewSet, PowerSourceViewSet, FuelTypeViewSet

router = DefaultRouter()
router.register(r'generationunit', GenerationUnitViewSet, basename = 'generationunit')
router.register(r'powersource', PowerSourceViewSet, basename = 'powersource')
router.register(r'fueltype', FuelTypeViewSet, basename = 'fueltype')

urlpatterns = [
  path('', include(router.urls))
]
