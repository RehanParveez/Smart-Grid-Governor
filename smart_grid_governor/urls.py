"""
URL configuration for smart_grid_governor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
  path('admin/', admin.site.urls),
  path('tokenobtain/', TokenObtainPairView.as_view(), name='token_obtain'),
  path('tokenrefresh/', TokenRefreshView.as_view(), name='token_refresh'),
  path('accounts/', include('accounts.urls')),
  path('topology/', include('topology.urls')),
  path('resources/', include('resources.urls')),
  path('economics/', include('economics.urls')),
  path('metering/', include('metering.urls')),
  path('prioritization/', include('prioritization.urls')),
  path('scheduler/', include('scheduler.urls'))
]
