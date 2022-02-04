from django.urls import path

from . import views
from .views import register_org

urlpatterns = [
    path('', views.signin, name='login'),
    path('login/', views.signin, name="login"),
    path('register/', views.signup, name="register"),
    path('logout/', views.signout, name="logout"),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('password_reset_confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path("full_register/", views.register_user_full, name="full_register"),
    path("register_org/", register_org, name="register_org"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
]
