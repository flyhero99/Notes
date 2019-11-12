import IPython
import os
import sys

import uuid
from django.db.models import Q
from django.shortcuts import render

# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from common_utils.permissions import BelongsToYouOrReadOnly
from common_utils.services import DCKernel
from common_utils.models import EntryEditor, Notebook, EntryEditorCheckpoint, EntryEditorFork
from common_utils.utils import make_cell, make_result_set, merge_cells
from entry_editor import serializers


class EntryEditorViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.EntryEditorSerializer
    queryset = EntryEditor.objects.all()
    filter_backends = (DjangoFilterBackend, SearchFilter)
    permission_classes = (BelongsToYouOrReadOnly,)
    search_fields = ('=id', 'name', 'word')

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(Q(user=self.request.user) | Q(is_public=True))
        else:
            return self.queryset.filter(is_public=True)

    def get_serializer_class(self):
        return {
            'list': serializers.EntryEditorListSerializer,
            'init': serializers.EntryEditorInitSerializer,
            'execute': serializers.EntryEditorExecuteSerializer
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

    @action(methods=['POST'], detail=True)
    def init(self, request, pk=None):
        entryeditor = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        word = serializer.validated_data['word']
        entryeditor.word = word
        entryeditor.status = 'NORMAL'
        if serializer.validated_data['empty']:
            entryeditor.cells = [
                {
                    'in': '',
                    'out': '',
                    'style': '',
                    'type': 'Code'
                }
            ]
        else:
            entryeditor.cells = [
            ]
            entryeditor.cells.append(make_cell('读音', '读音', {'font-size': '24px', 'level': 1}, 'Title'))
            entryeditor.cells.append(make_cell('', '[xxxxxx]', '', 'EditableText'))
            senses, _ = DCKernel.multi_synonyms(word, entryeditor.kernel_id)
            entryeditor.cells.append(make_cell('词义', '词义', {'font-size': '24px', 'level': 1}, 'Title'))
            for i, sense in enumerate(senses):
                sense_id = int(sense[0]['similarity'])
                entryeditor.cells.append(make_cell('词义id:{}'.format(sense_id), '词义id{}'.format(sense_id),
                                                   {'font-size': '20px', 'font-style': 'italic', 'level': 2}, 'Title'))
                entryeditor.cells.append(make_cell('释义', '释义', {'font-size': '18px', 'font-style': 'italic', 'level': 3},
                                                   'Title'))
                entryeditor.cells.append(make_cell('', '[自动生成]请手动补充', '', 'EditableText'))
                entryeditor.cells.append(make_cell('词义频', '词义频', {'font-size': '18px', 'font-style': 'italic', 'level': 3},
                                                   'Title'))
                entryeditor.cells.append(make_cell('sense_freq(word={}, sense_id={})'.format(word, sense_id),
                                                   make_result_set(
                                                       *DCKernel.sense_freq(word, i, entryeditor.kernel_id)),
                                                   {}, 'Code'))
                entryeditor.cells.append(make_cell('近义词', '近义词', {'font-size': '18px', 'font-style': 'italic', 'level': 3},
                                                   'Title'))
                entryeditor.cells.append(
                    make_cell('', ' '.join(map(lambda x: x['word'], sense)), {}, 'EditableText'))
                entryeditor.cells.append(make_cell('例句', '例句', {'font-size': '18px', 'font-style': 'italic', 'level': 3},
                                                   'Title'))
                for year in range(1986, 1996):
                    entryeditor.cells.append(make_cell(
                        'sense_examples(word={}, sense_id={}, year={}, offset=0, num=5)'.format(word, sense_id, year),
                        make_result_set(*DCKernel.sense_examples(word, i, year, 0, 5, entryeditor.kernel_id)), {},
                        'Code'))
        entryeditor.save()
        return Response(serializers.EntryEditorSerializer(entryeditor).data)

    @action(methods=['POST'], detail=True)
    def execute(self, request, pk=None):
        entryeditor = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        command = serializer.validated_data['command']
        ret, code = DCKernel.execute_command(entryeditor.kernel_id.hex, command)
        return Response(ret, code)

    @action(methods=['GET'], detail=True, url_path='diff/(?P<ee_pk>[^/.]+)')
    def diff(self, request, ee_pk, pk=None):
        ee1 = self.get_object()
        ee2 = get_object_or_404(self.get_queryset(), pk=ee_pk)
        if ee2.status != 'NORMAL':
            return Response({'detail': '无法合并。目标词条的状态为：'+ee2.status}, status=status.HTTP_400_BAD_REQUEST)
        return Response(merge_cells(ee1.cells, ee2.cells))


class EntryEditorCheckpointViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin,
                                   mixins.RetrieveModelMixin):
    serializer_class = serializers.EntryEditorCheckpointSerializer
    queryset = EntryEditorCheckpoint.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    filter_fields = ('entryeditor',)

    def get_serializer_class(self):
        return {
            'list': serializers.EntryEditorCheckpointListSerializer,
        }.get(self.action, self.serializer_class)


class EntryEditorForkViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin,
                             mixins.RetrieveModelMixin):
    serializer_class = serializers.EntryEditorForkSerializer
    queryset = EntryEditorFork.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    filter_fields = ('parent', 'child')

    def get_queryset(self):
        return self.queryset.filter(Q(parent__user=self.request.user) | Q(child__user=self.request.user))


class NotebookViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.NotebookSerializer
    queryset = Notebook.objects.all()
    permission_classes = (BelongsToYouOrReadOnly,)

    def get_queryset(self):
        return self.queryset.filter(Q(user=self.request.user) | Q(is_public=True))

    def get_serializer_class(self):
        return {
            'list': serializers.NotebookListSerializer,
            'execute': serializers.NotebookExecuteSerializer
        }.get(self.action, self.serializer_class)

    def perform_create(self, serializer):
        extra_params = {'user': self.request.user, 'kernel_id': uuid.uuid4()}
        if 'cells' not in serializer.validated_data:
            extra_params['cells'] = [
                {
                    'num': ' ',
                    'type': 'code',
                    'in': '',
                    'out': '',
                    'collapse': 'all',
                    'active_name': 'raw',
                }
            ]
        serializer.save(**extra_params)

    @action(methods=['POST'], detail=True)
    def execute(self, request, pk=None):
        notebook = self.get_object()
        if notebook.kernel_id is None:
            return Response({'detail': '请先连接一个内核'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        command = serializer.validated_data['command']
        ret, code = DCKernel.execute_command(notebook.kernel_id.hex, command)
        return Response(ret, code)

    @action(methods=['POST', 'GET', 'DELETE'], detail=True)
    def kernel(self, request, pk=None):
        notebook = self.get_object()
        if self.request.method == 'POST':
            notebook.kernel_id = uuid.uuid4()
            notebook.save()
            return Response({'kernel_id': notebook.kernel_id}, status=status.HTTP_201_CREATED)
        if self.request.method == 'GET':
            return Response({'kernel_id': notebook.kernel_id}, status=status.HTTP_200_OK)
        if self.request.method == 'DELETE':
            DCKernel.shutdown_kernel(notebook.kernel_id.hex)
            notebook.kernel_id = None
            notebook.save()
            return Response('', status=status.HTTP_204_NO_CONTENT)
        return Response({'detail': 'method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
