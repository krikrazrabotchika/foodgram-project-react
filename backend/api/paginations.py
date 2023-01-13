from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    """
    Переопределяем поле в кастомном пагинаторе:
    - название поля с количеством результатов в выдаче.
    """
    page_size_query_param = 'limit'
