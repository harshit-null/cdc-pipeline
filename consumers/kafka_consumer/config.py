import os

BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:19092")

GROUP_ID = os.environ.get("KAFKA_GROUP_ID", "cdc-consumer-group-v2")

TOPICS = [
    "cdc.cdc_db.ecommerce_product",
]

AUTO_OFFSET_RESET = "earliest"

