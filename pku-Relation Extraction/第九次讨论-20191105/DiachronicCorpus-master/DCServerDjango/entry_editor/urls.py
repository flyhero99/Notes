from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter

from entry_editor import views

router = DefaultRouter()
router.register(r'entryeditor', views.EntryEditorViewSet)
router.register(r'entryeditor_checkpoint', views.EntryEditorCheckpointViewSet)
router.register(r'notebook', views.NotebookViewSet)
router.register(r'entryeditor_fork', views.EntryEditorForkViewSet)
urlpatterns = [
    url(r'^', include(router.urls)),
]
