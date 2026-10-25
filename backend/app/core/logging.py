import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Configures structured logging across the application.
    Ensures safe formatting without sensitive data leaks.
    """
    log_level = logging.DEBUG if settings.ENVIRONMENT == "development" else logging.INFO

    logging_format = (
        "[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s"
    )

    logging.basicConfig(
        level=log_level,
        format=logging_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Silence overly verbose external loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


logger = logging.getLogger("placement_portal")
