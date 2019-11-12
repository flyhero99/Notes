from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from common_utils import views

router = DefaultRouter()
router.register(r'user', views.UserViewSet)
router.register(r'session', views.SessionViewSet, base_name='session')
urlpatterns = [
    url(r'^', include(router.urls)),
]
