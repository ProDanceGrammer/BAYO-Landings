import logging
import sys


def setup_logging(service_name: str) -> logging.Logger:
    """
    Configure structured logging for the service.

    Args:
        service_name: Name of the service (e.g., "landings", "core", "worker")

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    # Console handler with structured format
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Structured format: timestamp | service | level | message
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger