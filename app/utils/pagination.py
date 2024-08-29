from rest_framework.pagination import PageNumberPagination


class BasePagination(PageNumberPagination):
    page_size_query_param = "paginate"
    page_size = 10
