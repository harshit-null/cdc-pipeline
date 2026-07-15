try:
    from .handlers import handle_create, handle_update, handle_delete
    from .services.elasticsearch_service import elasticsearch_service
    from .logger import logger
except ImportError:
    from handlers import handle_create, handle_update, handle_delete
    from services.elasticsearch_service import elasticsearch_service
    from logger import logger


def route_event(event):
    op = event.get("op")

    if op == "c":
        product = handle_create(event)
        if product:
            elasticsearch_service.index_product(product)

    elif op == "u":
        product = handle_update(event)
        if product:
            elasticsearch_service.update_product(product)

    elif op == "d":
        product = handle_delete(event)
        if product:
            elasticsearch_service.delete_product(product.get("id"))

    elif op == "r":
        product = handle_create(event)  # Snapshot event
        if product:
            elasticsearch_service.index_product(product)

    else:
        logger.warning("Unknown operation: %s", op)