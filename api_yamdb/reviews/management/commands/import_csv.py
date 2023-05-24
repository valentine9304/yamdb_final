import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from users.models import User
from reviews.models import Title, Review, Comment
from catalog.models import Category, Genre

MODEL = {
    'category': Category,
    'genre': Genre,
    'titles': Title,
    'genre_title': 'genre_title',
    'users': User,
    'review': Review,
    'comments': Comment
}
BASE_DIR = settings.BASE_DIR


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csv', nargs='+', type=str)

    def handle(self, **options):
        file = options['csv'][0]
        csv_file = os.path.join(BASE_DIR, './static/data/' + file + '.csv')
        dataReader = csv.reader(
            open(csv_file, encoding='utf-8'),
            delimiter=',',
            quotechar='"'
        )
        next(dataReader)
        model = MODEL[file]

        if (file == 'category'
                or file == 'genre'
                or file == 'titles'
                or file == 'review'
                or file == 'comments'):
            try:
                print('Импорт ' + file + ':')
                for row in dataReader:
                    print('    ', *row)
                    obj = model(*row)
                    obj.save()
            except Exception as e:
                print(e)
        elif file == 'genre_title':
            print('Импорт ' + file + ':')
            for row in dataReader:
                print('    ', *row)
                title = Title.objects.get(id=row[1])
                genre = Genre.objects.get(id=row[2])
                title.genre.add(genre)
        else:
            print('Импорт ' + file + ':')
            for row in dataReader:
                print('    ', *row)
                obj = model(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    role=row[3],
                    bio=row[4],
                    first_name=row[5],
                    last_name=row[6]
                )
                obj.save()
