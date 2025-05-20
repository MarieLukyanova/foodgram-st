# Foodgram — Продуктовый помощник

Foodgram — это онлайн-сервис для публикации рецептов. Пользователи могут делиться любимыми блюдами, добавлять ингредиенты, сохранять рецепты в список покупок и формировать удобный PDF-файл со списком ингредиентов.

## Возможности

- Регистрация и авторизация пользователей
- Публикация рецептов с изображениями
- Добавление тегов и ингредиентов
- Фильтрация рецептов по тегам
- Добавление рецептов в избранное
- Формирование списка покупок
- Админ-панель

---

## Технологии

- Python 3.11
- Django + Django REST Framework
- PostgreSQL
- Docker + docker-compose
- Nginx
- Gunicorn
- GitHub Actions (CI)

---

## Структура проекта




## Инструкция для ревьюера

### Запуск проекта в Docker

1. Клонируйте репозиторий:
```bash
git clone https://github.com/<ваш-ник>/foodgram-project.git
cd foodgram-project
```
2. Обновите файл .env в папке infra/ со следующим содержимым со своими данными:
```
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=your_secret_key
DEBUG=False
```
3. Соберите и запустите контейнеры:

```bash
docker-compose -f infra/docker-compose.yml up -d --build
```
4. Выполнить миграции и создать суперпользователя:

```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```
5. Загрузить данные (опционально):

```bash
docker-compose exec backend python manage.py loaddata dump.json
```


## Доступы

API: http://localhost/api/

Документация API: http://localhost/api/docs/