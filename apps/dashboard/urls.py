from django.urls import path

from . import views
from . import map_views
from .views import analytics

urlpatterns = [

    path('', map_views.index, name='map'),
    path('full_map/', map_views.full_map, name='full_map'),
    path('drone/<plant_id>/<coordinate_xy>/', map_views.drone, name='drone'),
    path('full_map/drone/<plant_id>/<coordinate_xy>/', map_views.drone, name='drone'),

    path('tables/', views.tables, name='tables'),
    path('plantations/', views.plantations, name='plantations'),
    path('yield/', views.yields, name='yield'),
    path('nurseries/', views.nurseries, name='nurseries'),
    path('shipment/', views.shipment, name='shipment'),
    path("register_org/", views.register_org, name="register_org"),
    path("register_role/", views.register_role, name="register_role"),
    path('load_roles/', views.load_roles, name='load_roles'),
    path('profile/', views.profile, name='profile'),
    path('analytics/', analytics, name='analytics'),
]
