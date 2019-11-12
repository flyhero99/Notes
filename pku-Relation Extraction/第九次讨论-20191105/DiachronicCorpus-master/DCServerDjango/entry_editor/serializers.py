from rest_framework import serializers

from common_utils.models import EntryEditor, User, Notebook, EntryEditorCheckpoint, EntryEditorFork


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        ref_name = 'EntryEditor_UserSerializer'
        fields = ['id', 'username']


class EntryEditorSerializer(serializers.ModelSerializer):
    cells = serializers.JSONField(required=False)
    user = UserSerializer(read_only=True)
    # checkpoints = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = EntryEditor
        fields = '__all__'
        read_only_fields = ['user']


class EntryEditorListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = EntryEditor
        fields = ['id', 'name', 'user', 'is_public', 'created_at', 'updated_at']


class EntryEditorInitSerializer(serializers.Serializer):
    word = serializers.CharField()
    empty = serializers.BooleanField()


class EntryEditorExecuteSerializer(serializers.Serializer):
    command = serializers.CharField()


class EntryEditorCheckpointSerializer(serializers.ModelSerializer):
    cells_bak = serializers.JSONField()

    class Meta:
        model = EntryEditorCheckpoint
        fields = '__all__'


class EntryEditorForkSerializer(serializers.ModelSerializer):
    parent_ee = EntryEditorListSerializer(source='parent', read_only=True)
    child_ee = EntryEditorListSerializer(source='child', read_only=True)

    class Meta:
        model = EntryEditorFork
        fields = '__all__'


class EntryEditorCheckpointListSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntryEditorCheckpoint
        fields = ['id', 'entryeditor', 'created_at']


class NotebookSerializer(serializers.ModelSerializer):
    cells = serializers.JSONField(required=False)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Notebook
        fields = '__all__'
        read_only_fields = ['user']


class NotebookListSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    running = serializers.SerializerMethodField()

    class Meta:
        model = Notebook
        fields = ['id', 'name', 'user', 'is_public', 'created_at', 'updated_at', 'running']

    def get_running(self, obj):
        return obj.kernel_id is not None


class NotebookExecuteSerializer(serializers.Serializer):
    command = serializers.CharField()
