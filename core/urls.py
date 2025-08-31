"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Include trademind_app URLs
    path('', include('trademind_app.urls')),
    
    # Built-in auth (login/logout) - maps to Django's default views
    path('accounts/', include('django.contrib.auth.urls')),
    # 🔀 Redirect Django's default /accounts/profile/ to your dashboard
    path('accounts/profile/', RedirectView.as_view(
        pattern_name='trademind_app:dashboard',
        permanent=False)),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
