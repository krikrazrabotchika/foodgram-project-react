from api.paginations import CustomPagination
from api.permissions import IsAuthorAdminOrReadOnly
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import generics, permissions, response, status
from users.models import Follow, User
from users.serializers import FollowSerializer, UserDetailSerializer


class UserListViewSet(UserViewSet):
    """Вьюсет для отображения списка пользователей."""
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = (IsAuthorAdminOrReadOnly,)


class FollowListViewSet(generics.ListAPIView):
    """
    Вьюсет для отображения всех имеющихся у пользователя подписок.
    Доступность: только авторизованный пользователь.
    """
    serializer_class = FollowSerializer
    pagination_class = CustomPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(
            following__user=self.request.user
        ).annotate(recipes_count=Count('recipes'))


class FollowCreateDestroyViewSet(
    generics.CreateAPIView,
    generics.DestroyAPIView
):
    """
    Вьюсет для создания и удаления подписок на авторов.
    Доступность: только авторизованные пользователи.
    """
    serializer_class = FollowSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        if user_id == request.user.id:
            return response.Response(
                'Нельзя подписаться на себя самого.',
                status=status.HTTP_400_BAD_REQUEST
            )
        if Follow.objects.filter(
            user=request.user,
            author_id=user_id
        ).exists():
            return response.Response(
                'Вы уже подписаны на данного автора.',
                status=status.HTTP_400_BAD_REQUEST
            )
        author = get_object_or_404(User, id=user_id)
        Follow.objects.create(user=request.user, author_id=user_id)
        return response.Response(
            self.serializer_class(author, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        user_id = self.kwargs.get('user_id')
        follow = Follow.objects.filter(
            user=request.user,
            author_id=user_id
        )
        if follow:
            follow.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(
            'Вы не подписаны на данного автора.',
            status=status.HTTP_400_BAD_REQUEST
        )
