# see bottom of the page, https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
import os
import logging
import sys

from loguru import logger

# load log level thorugh environment
# TRACE 	5 	logger.trace()
# DEBUG 	10 	logger.debug()
# INFO 	20 	logger.info()
# SUCCESS 	25 	logger.success()
# WARNING 	30 	logger.warning()
# ERROR 	40 	logger.error()
# CRITICAL  50  logger.critical()
LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG"))

# option to emit json logs
JSON_LOGS = True if os.environ.get("JSON_LOGS", "0") == "1" else False


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    # intercept everything at the root logger
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel(LOG_LEVEL)

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # configure loguru
    logger.configure(handlers=[{"sink": sys.stdout, "serialize": JSON_LOGS}])
