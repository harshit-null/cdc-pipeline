from ..logger import logger


def handle_create(event):
    product = event.get("after")

    if not product:
        logger.warning("[CREATE] Missing 'after' payload.")
        return None

    logger.info("=" * 60)
    logger.info("CREATE EVENT")
    logger.info("Product ID   : %s", product.get("id"))
    logger.info("Product Name : %s", product.get("name"))

    return product