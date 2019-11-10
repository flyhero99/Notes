import uuid
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from rest_framework.filters import SearchFilter

from entry_editor.models import EntryEditor
from entry_editor.serializers import EntryEditorListSerializer, EntryEditorSerializer


# Create your views here.
class EntryEditorViewSet(viewsets.ModelViewSet):
    serializer_class = EntryEditorSerializer
    queryset = EntryEditor.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    search_fields = ('=id', 'name', 'word')

    def get_queryset(self):
        return self.queryset.filter(is_public=True)

    def get_serializer_class(self):
        return {
            'list': EntryEditorListSerializer,
        }.get(self.action, self.serializer_class)

    def perform_create(self, serializer):
        extra_params = {'user': self.request.user, 'kernel_id': uuid.uuid4()}
        if 'cells' not in serializer.validated_data:
            extra_params['cells'] = [
                {
                    'in': '',
                    'out': '',
                    'style': '',
                    'type': ''
                }
            ]
        if 'status' not in serializer.validated_data:
            extra_params['status'] = 'UNINITIALIZED'
        serializer.save(**extra_params)