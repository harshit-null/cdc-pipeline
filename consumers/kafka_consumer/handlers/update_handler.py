from logger import logger


def handle_update(event):
    product = event.get("after")

    if not product:
        logger.warning("[UPDATE] Missing 'after' payload.")
        return None

    logger.info("=" * 60)
    logger.info("UPDATE EVENT")
    logger.info("Product ID   : %s", product.get("id"))
    logger.info("Product Name : %s", product.get("name"))

    return product