from .models.cdc_event import CDCEvent
from .handlers import handle_create, handle_update, handle_delete
from .services.elasticsearch_service import elasticsearch_service
from .logger import logger


def route_event(event):
    cdc_event = CDCEvent.from_dict(event)

    if cdc_event.is_create:
        product = handle_create(event)

        if product:
            elasticsearch_service.index_product(product)

    elif cdc_event.is_update:
        product = handle_update(event)

        if product:
            elasticsearch_service.update_product(product)

    elif cdc_event.is_delete:
        product = handle_delete(event)

        if product:
            elasticsearch_service.delete_product(product.get("id"))

    elif cdc_event.is_snapshot:
        product = handle_create(event)

        if product:
            elasticsearch_service.index_product(product)

    else:
        logger.warning(
            "[ROUTER] Unknown CDC operation: %s",
            cdc_event.operation
        )