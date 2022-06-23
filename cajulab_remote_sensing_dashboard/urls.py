"""cajulab_remote_sensing_dashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from apps.dashboard import views

urlpatterns = i18n_patterns(
    path('admin/', admin.site.urls),
    path('', include('apps.authentication.urls'), name='Authentication'),
    path('dashboard/', include('apps.dashboard.urls'), name='Dashboard'),
)

urlpatterns += static(settings.STATIC_URL)

handler400 = views.error_400
handler403 = views.error_403
handler404 = views.error_404
handler500 = views.error_500
