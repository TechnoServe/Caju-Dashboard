from django.urls import path

from . import drone_views
from . import map_views
from . import views

urlpatterns = [
    path('', map_views.index, name='map'),
    path('drone/<plant_id>/<coordinate_xy>/', drone_views.drone, name='drone'),
    path('plantations/', views.plantations, name='plantations'),
    path('yield/', views.yields, name='yield'),
    path('nurseries/', views.nurseries, name='nurseries'),
    path('training/', views.training, name='training'),
    path('shipment/', views.shipment, name='shipment'),
    path("register_org/", views.register_org, name="register_org"),
    path("register_role/", views.register_role, name="register_role"),
    path('load_roles/', views.load_roles, name='load_roles'),
    path('profile/', views.profile, name='profile'),
    path('analytics/', views.analytics, name='analytics'),
    path('nut_count/', views.nut_count, name='nut_count'),
    path('defective_rate/', views.defective_rate, name='defective_rate'),
]
