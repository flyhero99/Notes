from rest_framework import serializers

from entry_editor.models import EntryEditor


class EntryEditorSerializer(serializers.ModelSerializer):
    cells = serializers.JSONField(required=False)

    class Meta:
        model = EntryEditor
        fields = '__all__'
        read_only_fields = ['user']


class EntryEditorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryEditor
        fields = ['id', 'name', 'user', 'is_public', 'created_at', 'updated_at']
