from django.contrib.auth import authenticate, login, logout
from rest_framework import mixins, status, viewsets, generics, permissions

# Create your views here.
from rest_framework.response import Response

from common_utils import serializers
from common_utils.models import User
from common_utils.permissions import IsAuthenticatedOrPOSTOnly


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    queryset = User.objects.all()
    permission_classes = (IsAuthenticatedOrPOSTOnly, )


class SessionViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin):
    serializer_class = serializers.SessionSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(request, username=serializer.validated_data['username'],
                                password=serializer.validated_data['password'])
            if user is not None:
                login(request, user)
                content = {
                    'user': serializers.UserSerializer(user).data,
                    'session': '',
                }
                return Response(content, status=status.HTTP_201_CREATED)
            return Response({'detail': '用户名或密码错误'}, status=status.HTTP_403_FORBIDDEN)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        user = request.user
        key = request.auth
        if not user.is_anonymous:
            user = serializers.UserSerializer(user).data
        else:
            user = []
        key = getattr(key, 'key', '')
        content = {
            'user': user,
            'session': key,
        }
        return Response(content)

    def destroy(self, request, *args, **kwargs):
        user = request.user
        if not user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        logout(request)
        return Response(status=status.HTTP_200_OK)
