import logging

from logging.config import dictConfig

import os

from enum import Enum

from typing import NewType



ENV_VAR = "WS_RPC_LOGGING"



class LoggingModes(Enum):

    NO_LOGS = 0

    UVICORN = 1

    SIMPLE = 2

    LOGURU = 3



LoggingMode = NewType('LoggingMode', LoggingModes)



class LoggingConfig:

    def __init__(self) -> None:

        self._mode = None



    config_template = {

        "version": 1,

        "disable_existing_loggers": True,

        "formatters": {

            "default": {

                "()": "uvicorn.logging.DefaultFormatter",

                "fmt": "%(levelprefix)s %(asctime)s %(message)s",

                "datefmt": "%Y-%m-%d %H:%M:%S",

            },

        },

        "handlers": {

            "default": {

                "formatter": "default",

                "class": "logging.StreamHandler",

            },

        },

        "loggers": {}

    }



    UVICORN_LOGGERS = {

        'uvicorn.error': {'propagate': False, 'handlers': ['default']},

        "fasterpc": {"handlers": ["default"], 'propagate': False, 'level': logging.INFO},

    }



    def get_mode(self):

        if self._mode is None:

            mode = LoggingModes.__members__.get(

                os.environ.get(ENV_VAR, "").upper(), LoggingModes.SIMPLE)

            self.set_mode(mode)

        return self._mode



    def set_mode(self, mode: LoggingMode = LoggingModes.UVICORN, level=logging.INFO):

        self._mode = mode

        logging_config = self.config_template.copy()

        if mode == LoggingModes.UVICORN:

            logging_config["loggers"] = self.UVICORN_LOGGERS.copy()

            logging_config["loggers"]["fasterpc"]["level"] = level

            dictConfig(logging_config)

        elif mode == LoggingModes.NO_LOGS:

            logging_config["loggers"] = {}

            dictConfig(logging_config)



logging_config = LoggingConfig()



def get_logger(name):

    mode = logging_config.get_mode()

    if mode == LoggingModes.LOGURU:

        from loguru import logger

    else:

        logger = logging.getLogger(f"fasterpc.{name}")

    return logger

