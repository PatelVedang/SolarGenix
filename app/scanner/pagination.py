from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

class PageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'paginate'
    max_page_size = 100