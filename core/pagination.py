from rest_framework.pagination import PageNumberPagination

class NormalDataPagination(PageNumberPagination):
    page_size = 10
    max_page_size = 50
    page_query_param = "page_size"


class LargeDataPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 200
    page_query_param = "page_size"
