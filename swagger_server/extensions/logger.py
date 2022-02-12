import os
import sys
import logging
from logging import StreamHandler


class Logger:
    """Logger class used to configure the flask logger"""

    @classmethod
    def configure_logger(cls) -> dict:
        """Configure the flask logger
        :return: dict
        """
        return {
            "version": os.getenv("VERSION", 1),
            "formatters": {"default": {"format": cls.verbose_formatter()}},
            "handlers": {
                "wsgi": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                }
            },
            "root": {"level": "INFO", "handlers": ["wsgi"]},
        }

    @classmethod
    def verbose_formatter(cls):
        """Get the verbose formatter used
        :return: str
        """
        return "[%(asctime)s]\t %(levelname)s\t[%(name)s.%(funcName)s:%(lineno)d]\t %(message)s"
