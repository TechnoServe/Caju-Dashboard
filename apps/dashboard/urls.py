from django.urls import path, include

from . import drone_views
from . import map_views
from . import views
from .views import analytics, nut_count, defective_rate

urlpatterns = [

    path('', map_views.index, name='map'),
    # path('drone/<plant_id>/<coordinate_xy>/<bounds>/', map_views.drone, name='drone'),
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
    path('analytics/', analytics, name='analytics'),
    path('nut_count/', nut_count, name='nut_count'),
    path('defective_rate/', defective_rate, name='defective_rate'),
]
