"""
Centralised logging configuration.

Usage anywhere in the project::

    from app.core.logging import get_logger

    logger = get_logger(__name__)
    logger.info("Something happened")

`configure_logging()` is called once at application startup (in `main.py`
via the lifespan handler).  Subsequent calls are no-ops because the root
logger is only configured the first time.
"""
import logging
import sys

_CONFIGURED = False

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging(level: int = logging.INFO) -> None:
    """
    Configure the root logger with a structured, human-readable format.

    Should be called once at application startup.  Calling it more than
    once is safe — subsequent calls are ignored.
    """
    global _CONFIGURED  # noqa: PLW0603
    if _CONFIGURED:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT))

    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    # Quieten noisy third-party loggers in production.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.

    Ensures `configure_logging()` has been called so the logger is always
    ready to use, even outside the FastAPI lifespan (e.g. in CLI scripts or
    Alembic migrations).
    """
    configure_logging()
    return logging.getLogger(name)
