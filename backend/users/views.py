from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from djoser.serializers import SetPasswordSerializer
from rest_framework.permissions import IsAuthenticated
from api.paginations import ApiPagination
from django.shortcuts import get_object_or_404
from time import time
from recipes.models import Follow
from .models import User
from .serializers import FollowSerializer, UserSerializer, AvatarSerializer
from api.permissions import IsCurrentUserOrAdminOrReadOnly


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsCurrentUserOrAdminOrReadOnly, )
    pagination_class = ApiPagination
    serializer_class = UserSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = self.request.user
        serializer = UserSerializer(user, context={'request': request})
        return Response(serializer.data)

    @action(["post"], detail=False, permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid(raise_exception=True):
            new_password = serializer.validated_data["new_password"]
            self.request.user.set_password(new_password)
            self.request.user.save()
            return Response('Пароль успешно изменен', status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, *args, **kwargs):
        author = get_object_or_404(User, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            serializer = FollowSerializer(data=request.data, context={'request': request, 'author': author})
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=author, user=user)
                return Response({'Подписка успешно создана': serializer.data}, status=status.HTTP_201_CREATED)
            return Response({'errors': 'Объект не найден'}, status=status.HTTP_404_NOT_FOUND)
        if Follow.objects.filter(author=author, user=user).exists():
            Follow.objects.get(author=author, user=user).delete()
            return Response( {'message': 'Успешная отписка', 'is_subscribed': False}, status=status.HTTP_200_OK)
        return Response({'errors': 'Объект не найден'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        follows = Follow.objects.filter(user=self.request.user)
        pages = self.paginate_queryset(follows)
        serializer = FollowSerializer(pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=[IsAuthenticated],
        parser_classes=[MultiPartParser, FormParser, JSONParser],
    )
    def upload_avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                avatar_url = f"{user.avatar.url}?{int(time())}"
                return Response({'message': 'Аватар обновлён', 'avatar_url': avatar_url}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            user.avatar.delete(save=True)
            user.save()
            return Response({'message': 'Аватар удалён'}, status=status.HTTP_200_OK)
