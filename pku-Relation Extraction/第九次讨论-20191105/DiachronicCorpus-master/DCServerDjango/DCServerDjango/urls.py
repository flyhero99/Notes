"""DCServerDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="DiachronicCorpus API",
        default_version='v0.1',
        description="历时语料库接口文档",
        terms_of_service="",
        contact=openapi.Contact(email="wuxian@pku.edu.cn"),
        license=openapi.License(name=""),
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^common/', include('common_utils.urls')),
    url(r'^entryeditor/', include('entry_editor.urls')),
    url(r'^corpus/', include('corpus.urls')),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name="swagger"),
]
