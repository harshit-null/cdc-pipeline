import os

from elasticsearch import Elasticsearch
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import get_search_service


es_client = Elasticsearch(
    os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
)

search_service = get_search_service(es_client)


class ProductSearchView(APIView):
    def get(self, request):
        result = search_service.search_products(
            query=request.query_params.get("q"),
            category=request.query_params.get("category"),
            min_price=request.query_params.get("min_price"),
            max_price=request.query_params.get("max_price"),
            is_active=request.query_params.get("is_active"),
            page=request.query_params.get("page", 1),
            page_size=request.query_params.get("page_size", 20),
            sort_by=request.query_params.get("sort_by", "updated_at"),
            sort_order=request.query_params.get("sort_order", "desc"),
        )

        return Response(result)