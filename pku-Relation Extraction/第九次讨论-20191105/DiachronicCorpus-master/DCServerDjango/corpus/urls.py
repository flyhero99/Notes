from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from corpus import views

router = DefaultRouter()
router.register(r'statistics', views.StatisticsViewSet, base_name='statistics')
router.register(r'sentence', views.SentenceViewSet, base_name='sentence')
urlpatterns = [
    url(r'^', include(router.urls)),
]
