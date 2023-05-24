from django.db import models

from .validators import validate_year


class Category(models.Model):
    name = models.CharField('Название категории', max_length=250)
    slug = models.SlugField(default='empty', unique=True,)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Название жанра', max_length=50)
    slug = models.SlugField(default='empty', unique=True,)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Название произведения', max_length=250)
    year = models.IntegerField(
        'Год издания',
        validators=[validate_year],
        db_index=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
    )
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Произвдение'
        verbose_name_plural = 'Произведения'
        ordering = ('-id',)

    def __str__(self):
        return self.name
