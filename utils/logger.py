import logging


def get_logger(name: str):

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s",
        "%H:%M:%S",
    )

    console = logging.StreamHandler()

    console.setFormatter(formatter)

    logger.addHandler(console)

    return logger