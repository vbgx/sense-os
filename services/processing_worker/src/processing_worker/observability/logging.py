import logging


def get_logger(name: str = "processing_worker"):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

# --- structured logging helpers -------------------------------------------------

# Keys reserved by Python logging.LogRecord
_RESERVED_LOGRECORD_KEYS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}


def safe_extra(extra: dict | None) -> dict:
    """
    Return a LogRecord-safe extra dict.
    - Renames reserved keys
    - Keeps values as-is
    """
    if not extra:
        return {}

    out: dict = {}
    for k, v in extra.items():
        key = str(k)
        if key in _RESERVED_LOGRECORD_KEYS:
            key = f"x_{key}"
        out[key] = v
    return out
