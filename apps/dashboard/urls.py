from django.urls import path, include

from . import drone_views
from . import map_views
from . import views
from .views import analytics, nut_count, defective_rate

search_patterns_plantations = [
    path('', views.plantations, name='plantations'),
    path('export_xls/', views.export_xls_plantations, name='export_xls_plantations'),
    path('export_csv/', views.export_csv_plantations, name='export_csv_plantations'),
    path('export_pdf/', views.export_pdf_plantations, name='export_pdf_plantations'),
]

search_patterns_nurseries = [
    path('', views.nurseries, name='nurseries'),
    path('export_xls/', views.export_xls_nurseries, name='export_xls_nurseries'),
    path('export_csv/', views.export_csv_nurseries, name='export_csv_nurseries'),
    path('export_pdf/', views.export_pdf_nurseries, name='export_pdf_nurseries'),
]

search_patterns_yields = [
    path('', views.yields, name='yield'),
    path('export_xls/', views.export_xls_yields, name='export_xls_yields'),
    path('export_csv/', views.export_csv_yields, name='export_csv_yields'),
    path('export_pdf/', views.export_pdf_yields, name='export_pdf_yields'),
]

search_patterns_training = [
    path('', views.training, name='training'),
    path('export_xls/', views.export_xls_training, name='export_xls_training'),
    path('export_csv/', views.export_csv_training, name='export_csv_training'),
    path('export_pdf/', views.export_pdf_training, name='export_pdf_training'),
]

urlpatterns = [

    path('', map_views.index, name='map'),
    # path('drone/<plant_id>/<coordinate_xy>/<bounds>/', map_views.drone, name='drone'),
    path('drone/<plant_id>/<coordinate_xy>/', drone_views.drone, name='drone'),
    path('plantations/', include(search_patterns_plantations)),
    path('yield/', include(search_patterns_yields)),
    path('nurseries/', include(search_patterns_nurseries)),
    path('training/', include(search_patterns_training)),
    path('shipment/', views.shipment, name='shipment'),
    path("register_org/", views.register_org, name="register_org"),
    path("register_role/", views.register_role, name="register_role"),
    path('load_roles/', views.load_roles, name='load_roles'),
    path('profile/', views.profile, name='profile'),
    path('analytics/', analytics, name='analytics'),
    path('nut_count/', nut_count, name='nut_count'),
    path('defective_rate/', defective_rate, name='defective_rate'),
]
