import json
from kafka.errors import KafkaError
from kafka import KafkaConsumer
from .router import route_event
from .config import (
    BOOTSTRAP_SERVERS,
    GROUP_ID,
    TOPICS,
    AUTO_OFFSET_RESET,
)
from .logger import logger


def log_banner(title):
    border = "=" * 72
    logger.info("%s", border)
    logger.info("[LIFECYCLE] %s", title)
    logger.info("%s", border)


def log_user_message(text):
    logger.info("[USER] %s", text)


def summarize_cdc_event(event):
    if not isinstance(event, dict):
        return "Received an event."

    op = event.get("op")
    after = event.get("after") or {}
    before = event.get("before") or {}

    product_name = after.get("name") or before.get("name")
    sku = after.get("sku") or before.get("sku")
    item_label = product_name or sku or "a product"

    if op == "c":
        return f"New product created: {item_label}."
    if op == "u":
        return f"Product updated: {item_label}."
    if op == "d":
        return f"Product deleted: {item_label}."
    if op == "r":
        return f"Snapshot event received for {item_label}."
    return "Unknown CDC event."

def value_deserializer(message):
    """Deserialize Kafka message value."""
    if message is None:
        return None

    return json.loads(message.decode("utf-8"))


def start_consumer():
    """
    Creates a Kafka consumer and continuously listens
    for Debezium CDC events.
    """

    consumer = None

    try:
        consumer = KafkaConsumer(
            *TOPICS,
            bootstrap_servers=BOOTSTRAP_SERVERS,
            group_id=GROUP_ID,
            auto_offset_reset=AUTO_OFFSET_RESET,
            enable_auto_commit=True,
            value_deserializer=value_deserializer,
        )
        logger.info("Subscription: %s", consumer.subscription())
        logger.info("Bootstrap connected.")
        consumer.topics()
        consumer.poll(timeout_ms=1000)

        logger.info("Assignment: %s", consumer.assignment())
        logger.info("Available topics: %s", consumer.topics())

        log_banner("Kafka Consumer Started")
        logger.info("[START] Broker : %s", BOOTSTRAP_SERVERS)
        logger.info("[START] Group  : %s", GROUP_ID)
        logger.info("[START] Topics : %s", ", ".join(TOPICS))
        log_user_message("Consumer is running and waiting for database changes.")

        # for message in consumer:
        while True:
            message = next(consumer)
            logger.info("MESSAGE RECEIVED!")

            # Debezium tombstone record
            if message.value is None:
                logger.warning(
                    "[TOMBSTONE] topic=%s partition=%s offset=%s",
                    message.topic,
                    message.partition,
                    message.offset,
                )
                log_user_message("Delete cleanup event received (tombstone).")
                continue

            logger.info("%s", "-" * 72)
            logger.info(
                "[EVENT] topic=%s partition=%s offset=%s key=%s",
                message.topic,
                message.partition,
                message.offset,
                message.key,
            )
            log_user_message(summarize_cdc_event(message.value))

            route_event(message.value)

    except KafkaError:
        logger.exception("[ERROR] Kafka error occurred while consuming messages.")
        log_user_message("Could not read events from Kafka due to a connection or broker issue.")

    except KeyboardInterrupt:
        logger.info("[STOP] Keyboard interrupt received. Stopping consumer...")
        log_user_message("Consumer stopped by user.")

    except Exception:
        logger.exception("[ERROR] Unexpected error in Kafka consumer.")
        log_user_message("Consumer stopped because of an unexpected error.")

    finally:
        if consumer is not None:
            consumer.close()

        log_banner("Kafka Consumer Stopped")
        log_user_message("Consumer shutdown is complete.")