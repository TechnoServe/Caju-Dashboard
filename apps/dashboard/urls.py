from django.urls import path

from . import views
from .views import analytics, nut_count, defective_rate

urlpatterns = [

    # The home page
    path('', views.index, name='map'),
    path('full_map/', views.full_map, name='full_map'),
    # path('map/full_map/', views.full_map, name='full_map'),
    path('tables/', views.tables, name='tables'),
    path('plantations/', views.plantations, name='plantations'),
    path('yield/', views.yields, name='yield'),
    path('nurseries/', views.nurseries, name='nurseries'),
    path('shipment/', views.shipment, name='shipment'),
    path('drone/<plant_id>/<coordinate_xy>/', views.drone, name='drone'),
    path('full_map/drone/<plant_id>/<coordinate_xy>/', views.drone, name='drone'),
    path("register_org/", views.register_org, name="register_org"),
    path("register_role/", views.register_role, name="register_role"),
    path('load_roles/', views.load_roles, name='load_roles'),
    path('profile/', views.profile, name='profile'),
    path('analytics/', analytics, name='analytics'),
    path('nut_count/', nut_count, name='nut_count'),
    path('defective_rate/', defective_rate, name='defective_rate'),
]
