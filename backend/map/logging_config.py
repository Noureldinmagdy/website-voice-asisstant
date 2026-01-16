import logging

def setup_logging(level=logging.INFO):
    if logging.getLogger().handlers:
        return  # يمنع تكرار الـ handlers

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
