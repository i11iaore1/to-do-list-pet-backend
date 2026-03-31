from rest_framework.pagination import PageNumberPagination, Response


class BasePageNumberDataPagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.page.paginator.count,
                "current": self.page.number,
                "next": self.page.next_page_number() if self.page.has_next() else None,
                "prev": (
                    self.page.previous_page_number()
                    if self.page.has_previous()
                    else None
                ),
                "total_pages": self.page.paginator.num_pages,
                "results": data,
            }
        )


class NormalDataPagination(BasePageNumberDataPagination):
    page_size = 10
    max_page_size = 50


class LargeDataPagination(BasePageNumberDataPagination):
    page_size = 50
    max_page_size = 100
