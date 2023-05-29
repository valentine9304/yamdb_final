![workflow](https://github.com/valentine9304/yamdb_final/workflows/yamdb_workflow.yaml/badge.svg)

```
Проэкт развернут по адресу http://84.252.128.99/api/v1/
```

 Проект YaMDb
Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.Произведения делятся на категории, такие как «Книги», «Фильмы», «Музыка».Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти (целое число). Пользователи могут оставлять комментарии к отзывам. Из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число).

# REST API для сервиса **YamDb** 
версия c Docker, Continuous Integration на GitHub Actions

## Ресурсы API YaMDb
+ Ресурс auth: аутентификация.
+ Ресурс users: пользователи.
+ Ресурс titles: произведения, к которым пишут отзывы (определённый фильм, книга или песенка).
+ Ресурс categories: категории (типы) произведений («Фильмы», «Книги», «Музыка»). Одно произведение может быть привязано только к одной категории.
+ Ресурс genres: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
+ Ресурс reviews: отзывы на произведения. Отзыв привязан к определённому произведению.
+ Ресурс comments: комментарии к отзывам. Комментарий привязан к определённому отзыву.

## Стек технологий

+ Python
+ Django
+ DRF
+ Simple JWT

## Пользовательские роли
+ Аноним — может просматривать описания произведений, читать отзывы и комментарии.
+ Аутентифицированный пользователь (user) — может, как и Аноним, читать всё, дополнительно он может публиковать отзывы и ставить оценку произведениям (фильмам/книгам/песенкам), может комментировать чужие отзывы; может редактировать и удалять свои отзывы и комментарии. Эта роль присваивается поq умолчанию каждому новому пользователю.
+ Модератор (moderator) — те же права, что и у Аутентифицированного пользователя плюс право удалять любые отзывы и комментарии.
+ Администратор (admin) — полные права на управление всем контентом проекта. Может создавать и удалять произведения, категории и жанры. Может назначать роли пользователям.

### Установка Docker
Установите Docker, используя инструкции с официального сайта:
- для [Windows и MacOS](https://www.docker.com/products/docker-desktop)
- для [Linux](https://docs.docker.com/engine/install/ubuntu/). Отдельно потребуется установть [Docker Compose](https://docs.docker.com/compose/install/)

### Запуск проекта (на примере Linux)

- Создайте на своем компютере папку проекта YamDb `mkdir yamdb` и перейдите в нее `cd yamdb`
- Склонируйте этот репозиторий в текущую папку `git clone git@github.com:valentine9304/yamdb_final.git .`
- Создайте файл `.env` командой `touch .env` и добавьте в него переменные окружения для работы с базой данных:
```
DB_NAME=postgres # имя базы данных
POSTGRES_USER=postgres # логин для подключения к базе данных
POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД 
```

Перейти в папку infra и запустить docker-compose.yaml
(при установленном и запущенном Docker)
```
cd yamdb_final/infra
docker-compose up
```

Для пересборки контейнеров выполнять команду:
(находясь в папке infra, при запущенном Docker)
```
docker-compose up -d --build
```

Создать суперпользователя:

```
docker-compose exec web python manage.py createsuperuser
```

Проверьте работоспособность приложения, для этого перейдите на страницу:
```
http://84.252.128.99/admin/
http://84.252.128.99/api/v1/
```

## Деплой на удаленный сервер
Для запуска проекта на удаленном сервере необходимо:
- скопировать на сервер файлы `docker-compose.yaml`, `.env` и папку `nginx` командами:
```
scp docker-compose.yaml  <user>@<server-ip>:
scp .env <user>@<server-ip>:
scp -r nginx/ <user>@<server-ip>:

```
- создать переменные окружения в разделе `secrets` настроек текущего репозитория:
```
DOCKER_PASSWORD # Пароль от Docker Hub
DOCKER_USERNAME # Логин от Docker Hub
HOST # Публичный ip адрес сервера
USER # Пользователь зарегистрированный на сервере
PASSPHRASE # Если ssh-ключ защищен фразой-паролем
SSH_KEY # Приватный ssh-ключ
TELEGRAM_TO # ID телеграм-аккаунта
TELEGRAM_TOKEN # Токен бота
```

### После каждого обновления репозитория (`git push`) будет происходить:
1. Проверка кода на соответствие стандарту PEP8 (с помощью пакета flake8) и запуск pytest из репозитория yamdb_final
2. Сборка и доставка докер-образов на Docker Hub.
3. Автоматический деплой.
4. Отправка уведомления в Telegram.

### Примеры API запросов:
+ [POST] /api/v1/auth/signup/ - Регистрация нового пользователя
```json
    "username": "user@mail.ru",
    "email": "user@mail.ru"
```
+ [POST] /api/v1/auth/token/ - Выдача jwt token Пользавтелю. 
```json
    "username": "user",
    "confirmation_code": "bj7rvg-ec9c545473ddd3fca5e1f1bf782efa0f"
```
+ [POST] /api/v1/titles/{title_id}/reviews/ - Добавить новый отзыв. Пользователь может оставить только один отзыв на произведение.
```json
    "text": "string",
    "score": 1
```
+ [POST] /api/v1/titles/{title_id}/reviews/{review_id}/comments/ - Добавить новый комментарий для отзыва.
```json
    "text": "string"
```

## Авторы
:bowtie: Александр  
:trollface: Валентин  
:sunglasses: Семён
