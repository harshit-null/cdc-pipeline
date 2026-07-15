import os

from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError
from elasticsearch import ApiError

DEV_MODE = os.environ.get("DEV_MODE", "true").lower() == "true"

try:
    from ..logger import logger
except ImportError:
    from logger import logger


class ElasticsearchService:
    """
    Service responsible for interacting with Elasticsearch.
    """

    def __init__(self):
        self.es_url = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
        self.index_name = os.environ.get("ELASTICSEARCH_INDEX", "products")
        self.refresh_mode = "wait_for" if DEV_MODE else False
        self.client = Elasticsearch(self.es_url)
        logger.info("Elasticsearch connected: %s", self.client.ping())
        if self.client.ping():
            logger.info("[ELASTICSEARCH] Connected to %s", self.es_url)
        else:
            logger.error("[ELASTICSEARCH] Could not connect to %s", self.es_url)

    def _normalize_product(self, product):
        """Normalize Debezium payload values to match Elasticsearch mapping types."""
        normalized = dict(product)

        if "id" in normalized and normalized["id"] is not None:
            normalized["id"] = int(normalized["id"])

        if "stock_quantity" in normalized and normalized["stock_quantity"] is not None:
            normalized["stock_quantity"] = int(normalized["stock_quantity"])

        if "price" in normalized and normalized["price"] is not None:
            normalized["price"] = float(normalized["price"])

        if "is_active" in normalized and normalized["is_active"] is not None:
            value = normalized["is_active"]
            if isinstance(value, str):
                normalized["is_active"] = value.strip().lower() in ("1", "true", "t", "yes")
            else:
                normalized["is_active"] = bool(value)

        if "created_at" in normalized and normalized["created_at"] is not None:
            normalized["created_at"] = int(normalized["created_at"])

        if "updated_at" in normalized and normalized["updated_at"] is not None:
            normalized["updated_at"] = int(normalized["updated_at"])

        return normalized

    def index_product(self, product):
        if not product:
            logger.warning("[ELASTICSEARCH] Cannot index empty product payload.")
            return None

        product_id = product.get("id")
        if product_id is None:
            logger.warning("[ELASTICSEARCH] Missing product id for index operation.")
            return None

        normalized_product = self._normalize_product(product)

        logger.info("=" * 60)
        logger.info("[ELASTICSEARCH] INDEX PRODUCT")
        logger.info("ID   : %s", product_id)
        logger.info("Name : %s", product.get("name"))
        logger.info("=" * 60)

        try:
            response = self.client.index(
                index=self.index_name,
                id=str(product_id),
                document=normalized_product,
                refresh=self.refresh_mode,
            )
            logger.info("Response from Elasticsearch: %s", response)
            logger.info("[ELASTICSEARCH] Indexed result: %s", response.get("result"))
            return response
        except ApiError as e:
            logger.error("[ELASTICSEARCH] Error indexing product: %s", e)
            return None


    def update_product(self, product):
        if not product:
            logger.warning("[ELASTICSEARCH] Cannot update empty product payload.")
            return None

        product_id = product.get("id")
        if product_id is None:
            logger.warning("[ELASTICSEARCH] Missing product id for update operation.")
            return None

        normalized_product = self._normalize_product(product)

        logger.info("=" * 60)
        logger.info("[ELASTICSEARCH] UPDATE PRODUCT")
        logger.info("ID   : %s", product_id)
        logger.info("Name : %s", product.get("name"))
        logger.info("=" * 60)

        try:
            response = self.client.update(
                index=self.index_name,
                id=str(product_id),
                doc=normalized_product,
                doc_as_upsert=True,
                refresh=self.refresh_mode,
            )
            logger.info("[ELASTICSEARCH] Updated result: %s", response.get("result"))
            return response
        except ApiError as e:
            logger.error("[ELASTICSEARCH] Error updating product: %s", e)
            return None


    def delete_product(self, product_id):
        if product_id is None:
            logger.warning("[ELASTICSEARCH] Missing product id for delete operation.")
            return None

        logger.info("=" * 60)
        logger.info("[ELASTICSEARCH] DELETE PRODUCT")
        logger.info("ID : %s", product_id)
        logger.info("=" * 60)

        try:
            response = self.client.delete(
                index=self.index_name,
                id=str(product_id),
                refresh=self.refresh_mode,
            )
            logger.info("[ELASTICSEARCH] Deleted result: %s", response.get("result"))
            return response
        except NotFoundError:
            logger.warning("[ELASTICSEARCH] Product id=%s not found in index.", product_id)
            return None


elasticsearch_service = ElasticsearchService()