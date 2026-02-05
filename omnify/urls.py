"""
URL configuration for omnify project.

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
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import HomeView, DashboardView
from apps.items.views import ItemListView, ItemDetailView, item_create, item_edit
from apps.locations.views import LocationListView, LocationDetailView, location_create, location_edit

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # Items
    path('items/', ItemListView.as_view(), name='item_list'),
    path('items/<uuid:pk>/', ItemDetailView.as_view(), name='item_detail'),
    path('items/create/', item_create, name='item_create'),
    path('items/<uuid:pk>/edit/', item_edit, name='item_edit'),
    
    # Locations
    path('locations/', LocationListView.as_view(), name='location_list'),
    path('locations/<uuid:pk>/', LocationDetailView.as_view(), name='location_detail'),
    path('locations/create/', location_create, name='location_create'),
    path('locations/<uuid:pk>/edit/', location_edit, name='location_edit'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
