from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Avg
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import IntegrityError

from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework import mixins, status, viewsets, permissions
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.decorators import action

from catalog.models import Category, Genre, Title
from .serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleCreateSerializer,
    TitleSerializer
)
from .permissions import IsAdminOrReadOnly
from .mixins import ReviewGenreModelMixin
from .filters import TitleFilter
from users.models import User
from .serializers import SignUpSerializer, TokenSerializer, UserSerializer
from .permissions import IsAdmin
from api_yamdb.settings import EMAIL_HOST_USER

from reviews.models import Comment
from api.permissions import IsAuthorOrAdminOrModerator
from api.serializers import (
    ReviewSerializer,
    CommentSerializer
)


class CategoryViewSet(ReviewGenreModelMixin):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name',)
    pagination_class = PageNumberPagination
    lookup_field = 'slug'


class GenreViewSet(ReviewGenreModelMixin):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [SearchFilter]
    search_fields = ['name']
    pagination_class = PageNumberPagination
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(
        rating=Avg('reviews__score')
    ).select_related('category').prefetch_related('genre')
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializer
        return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrAdminOrModerator
    ]
    pagination_class = LimitOffsetPagination

    def __get_title(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title

    def get_queryset(self):
        title = self.__get_title()
        new_queryset = title.reviews.all().select_related('author')
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.__get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев."""

    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrAdminOrModerator
    ]
    pagination_class = LimitOffsetPagination

    def __get_title(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title

    def __get_review(self):
        title = self.__get_title()
        review = (title.reviews.get(pk=self.kwargs.get('review_id')))
        return review

    def get_queryset(self):
        request_title = self.__get_title()
        request_review = self.__get_review()
        new_queryset = Comment.objects.select_related('author').filter(
            title=request_title,
            review=request_review
        )
        return new_queryset

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.__get_title(),
            review=self.__get_review()
        )


class SignUpViewSet(mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    """Вьюсет для регистрации новых пользавотелей."""

    queryset = User.objects.all()
    serializer_class = SignUpSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        """Регистрируем нового пользователя и отправляем
        ему на почту код подтверждения"""

        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, _ = User.objects.get_or_create(**serializer.validated_data)
        except IntegrityError:
            return Response("Проблемы", status=status.HTTP_400_BAD_REQUEST)
        confirmation_code = default_token_generator.make_token(user)
        send_mail('Код подтверждения регистрации api_yamdb',
                  f'Ваш код подтверждения: {confirmation_code}',
                  EMAIL_HOST_USER,
                  [user.email],
                  fail_silently=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenViewSet(mixins.CreateModelMixin,
                   viewsets.GenericViewSet):
    """Получает confirmation_code от Пользователя и отдаёт JWT Token."""

    queryset = User.objects.all()
    serializer_class = TokenSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        """Предоставляет пользователю JWT токен по коду подтверждения."""

        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_object_or_404(
            User, username=serializer.validated_data['username'])

        if not default_token_generator.check_token(
                user, serializer.validated_data['confirmation_code']):
            message = 'Неверный confirmation_code'
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {f'JWT Токен пользователя {user}': str(
            AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Предоставляет Админу информацию о Пользователях."""
    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'patch', 'delete']
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    filter_backends = [SearchFilter]
    search_fields = ['username']
    permission_classes = [IsAdmin]

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        if request.method == 'GET':
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        if request.method == 'PATCH':
            user = get_object_or_404(User, id=request.user.id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save(role=request.user.role)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
