import logging
import sys


def configure_logging(service_name: str, log_level: str = "INFO") -> None:
    level = getattr(logging, log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=level,
        format=f"%(asctime)s | %(levelname)s | {service_name} | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
