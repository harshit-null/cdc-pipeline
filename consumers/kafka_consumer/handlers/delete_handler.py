from ..logger import logger


def handle_delete(event):
    product = event.get("before")

    if not product:
        logger.warning("[DELETE] Missing 'before' payload.")
        return None

    logger.info("=" * 60)
    logger.info("DELETE EVENT")
    logger.info("Product ID   : %s", product.get("id"))
    logger.info("Product Name : %s", product.get("name"))

    return product