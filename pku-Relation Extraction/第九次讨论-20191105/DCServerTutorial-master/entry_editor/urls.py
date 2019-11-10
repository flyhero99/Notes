from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from entry_editor import views

router = DefaultRouter()
router.register(r'entryeditor', views.EntryEditorViewSet)
urlpatterns = [
    url(r'^', include(router.urls)),
]
