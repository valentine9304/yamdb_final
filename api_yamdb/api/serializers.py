from catalog.models import Category, Genre, Title
from django.core.validators import MaxValueValidator, MinValueValidator

from rest_framework import serializers

from users.models import User
from reviews.models import Review, Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели Review (Отзывы)."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )
    score = serializers.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ]
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        if Review.objects.filter(
                author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Можно написать только один отзыв для этого произведения!'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели Comment (Комментарии)."""

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class SignUpSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""
    username = serializers.RegexField(
        regex=r'^[\w@.+-_]+$',
        max_length=150,
        required=True,
    )
    email = serializers.EmailField(
        max_length=150,
        required=True
    )

    class Meta:
        model = User
        fields = (
            'username', 'email'
        )

    def validate(self, data):
        """Запрет на регистрацию c логином Me."""
        if data['username'] == data['email']:
            raise serializers.ValidationError(
                'Использование одинакого Логина и E-mail запрещено.'
            )

        if data['username'] == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве Логина запрещено.'
            )
        return data


class TokenSerializer(serializers.Serializer):
    """Сериализатор получения JWT-токена в обмен
    на username и confirmation code."""

    username = serializers.RegexField(
        regex=r'^[\w@.+-_]+$',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True
    )


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""
    class Meta:
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role',)
        model = User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id', )
        ordering = ['-id']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id', )
        ordering = ['-id']


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category',)
        model = Title
        ordering = ['-id']


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        fields = '__all__'
        model = Title
        ordering = ['-id']
