import logging


class HighlightFormatter(logging.Formatter):
    """Adds ANSI colors and keeps logs compact and readable."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    COLORS = {
        logging.DEBUG: "\033[36m",     # cyan
        logging.INFO: "\033[32m",      # green
        logging.WARNING: "\033[33m",   # yellow
        logging.ERROR: "\033[31m",     # red
        logging.CRITICAL: "\033[41m",  # red background
    }

    def format(self, record):
        base = super().format(record)
        color = self.COLORS.get(record.levelno, "")
        return f"{self.BOLD}{color}{base}{self.RESET}"


def build_logger():
    logger_instance = logging.getLogger("kafka-consumer")
    logger_instance.setLevel(logging.INFO)
    logger_instance.propagate = False

    if logger_instance.handlers:
        return logger_instance

    handler = logging.StreamHandler()
    formatter = HighlightFormatter("%(asctime)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    logger_instance.addHandler(handler)
    return logger_instance


logger = build_logger()