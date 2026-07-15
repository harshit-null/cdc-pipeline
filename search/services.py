import os

from elasticsearch import ApiError
from elasticsearch import NotFoundError


class SearchService:
    """Encapsulates product read/search operations from Elasticsearch."""

    def __init__(self, es_client, index_name=None):
        self.es_client = es_client
        self.index_name = index_name or os.environ.get("ELASTICSEARCH_INDEX", "products")

    def get_product(self, product_id):
        """Fetch one product by document id."""
        try:
            response = self.es_client.get(index=self.index_name, id=str(product_id))
            return response.get("_source")
        except NotFoundError:
            return None

    def search_products(
        self,
        query=None,
        category=None,
        min_price=None,
        max_price=None,
        is_active=None,
        page=1,
        page_size=20,
        sort_by="updated_at",
        sort_order="desc",
    ):
        """Search products with keyword + structured filters and pagination."""
        allowed_sort_fields = {"price", "name", "created_at", "updated_at"}
        if sort_by not in allowed_sort_fields:
            sort_by = "updated_at"

        if sort_order not in {"asc", "desc"}:
            sort_order = "desc"

        page = max(1, int(page))
        page_size = max(1, min(int(page_size), 100))
        offset = (page - 1) * page_size

        must = []
        filters = []

        if query:
            must.append(
                {
                    "multi_match": {
                        "query": query,
                        "fields": ["name^3", "description", "sku^2", "category"],
                        "type": "best_fields",
                        "operator": "and",
                    }
                }
            )

        if category:
            filters.append({"term": {"category": category}})

        if min_price is not None or max_price is not None:
            price_range = {}
            if min_price is not None:
                price_range["gte"] = float(min_price)
            if max_price is not None:
                price_range["lte"] = float(max_price)
            filters.append({"range": {"price": price_range}})

        if is_active is not None:
            if isinstance(is_active, str):
                is_active = is_active.strip().lower() in ("true", "1")
            filters.append({"term": {"is_active": bool(is_active)}})

        body = {
            "from": offset,
            "size": page_size,
            "query": {
                "bool": {
                    "must": must if must else [{"match_all": {}}],
                    "filter": filters,
                }
            },
            "sort": [{sort_by: {"order": sort_order}}],
        }

        try:
            response = self.es_client.search(index=self.index_name, body=body)
            hits = response.get("hits", {})
            total = hits.get("total", {}).get("value", 0)
            items = [
                {
                    "id": hit.get("_id"),
                    "score": hit.get("_score"),
                    **hit.get("_source", {}),
                }
                for hit in hits.get("hits", [])
            ]
            return {
                "total": total,
                "page": page,
                "page_size": page_size,
                "items": items,
            }
        except ApiError as exc:
            return {
                "total": 0,
                "page": page,
                "page_size": page_size,
                "items": [],
                "error": str(exc),
            }

    def suggest_names(self, prefix, limit=10):
        """Return lightweight product name suggestions for autocomplete."""
        if not prefix:
            return []

        limit = max(1, min(int(limit), 25))
        body = {
            "size": limit,
            "query": {
                "match_phrase_prefix": {
                    "name": {
                        "query": prefix,
                    }
                }
            },
            "_source": ["name"],
        }

        try:
            response = self.es_client.search(index=self.index_name, body=body)
            names = []
            seen = set()
            for hit in response.get("hits", {}).get("hits", []):
                name = hit.get("_source", {}).get("name")
                if name and name not in seen:
                    seen.add(name)
                    names.append(name)
            return names
        except ApiError:
            return []


def get_search_service(es_client, index_name=None):
    return SearchService(es_client=es_client, index_name=index_name)

   