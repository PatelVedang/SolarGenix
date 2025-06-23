from rest_framework.pagination import PageNumberPagination


class BasePagination(PageNumberPagination):
    """
    Custom pagination class that extends DRF's PageNumberPagination.

    Attributes:
        page_size_query_param (str): The name of the query parameter used to specify the page size. Defaults to "paginate".
        page_size (int): The default number of items to include on each page. Defaults to 10.
    """

    page_size_query_param = "paginate"
    page_size = 10
