"""
URL configuration for sistem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from makale_ekleme import views as makaleviews
from editor_actions import views as editorviews

urlpatterns = [
    path('admin/', admin.site.urls),
    path('makale_olustur/', makaleviews.makale_olustur, name='makale_olustur'),
    path('yonetici/', editorviews.editor, name='yonetici'),
    path('makale/<int:makale_id>/', editorviews.makale_detay, name='makale_detay'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
