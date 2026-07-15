import os
from datetime import datetime, timezone
from decimal import Decimal

from django.core.management.base import BaseCommand
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from ecommerce.models import Product


def to_epoch_micros(value):
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return int(value.timestamp() * 1_000_000)


def normalize_product(product):
    return {
        "id": int(product.id),
        "name": product.name,
        "description": product.description or "",
        "category": product.category,
        "sku": product.sku,
        "price": float(product.price if isinstance(product.price, Decimal) else Decimal(product.price)),
        "stock_quantity": int(product.stock_quantity),
        "is_active": bool(product.is_active),
        "created_at": to_epoch_micros(product.created_at),
        "updated_at": to_epoch_micros(product.updated_at),
    }


class Command(BaseCommand):
    help = "Backfill existing Product rows from MySQL to Elasticsearch"

    def add_arguments(self, parser):
        parser.add_argument(
            "--index",
            default=os.environ.get("ELASTICSEARCH_INDEX", "products"),
            help="Target Elasticsearch index name",
        )
        parser.add_argument(
            "--es-url",
            default=os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200"),
            help="Elasticsearch URL",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Number of products per bulk chunk",
        )

    def handle(self, *args, **options):
        index_name = options["index"]
        es_url = options["es_url"]
        batch_size = max(1, options["batch_size"])

        es_client = Elasticsearch(es_url)
        if not es_client.ping():
            self.stderr.write(self.style.ERROR(f"Could not connect to Elasticsearch at {es_url}"))
            return

        total_products = Product.objects.count()
        if total_products == 0:
            self.stdout.write(self.style.WARNING("No products found to backfill."))
            return

        self.stdout.write(
            self.style.NOTICE(
                f"Starting backfill: {total_products} products -> index '{index_name}'"
            )
        )

        def actions():
            queryset = Product.objects.all().order_by("id").iterator(chunk_size=batch_size)
            for product in queryset:
                source = normalize_product(product)
                yield {
                    "_op_type": "index",
                    "_index": index_name,
                    "_id": str(product.id),
                    "_source": source,
                }

        success_count, errors = bulk(
            es_client,
            actions(),
            chunk_size=batch_size,
            raise_on_error=False,
            refresh="wait_for",
        )

        self.stdout.write(self.style.SUCCESS(f"Indexed/updated documents: {success_count}"))

        if errors:
            self.stderr.write(self.style.ERROR(f"Bulk errors: {len(errors)}"))
            for err in errors[:5]:
                self.stderr.write(str(err))
        else:
            self.stdout.write(self.style.SUCCESS("Backfill completed with no errors."))
