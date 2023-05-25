# -*- coding: utf-8 -*-

import logging
import colorlog

"""
file:
description:
language: python3 3.11.3
author: @Xiaoyu Tongyang, fengkeyleaf@gmail.com
        Personal website: https://fengkeyleaf.com
"""


# https://docs.python.org/3/library/logging.html#logging-levels
# https://github.com/borntyping/python-colorlog
def get_logger( ll: int, n: str = __name__ ) -> logging.Logger:
    """

    @param ll: logging level
    @return:
    """
    # Create a logger
    logger: logging.Logger = colorlog.getLogger( n )
    logger.setLevel( ll )

    # # Create a console handler and set its level
    handler: colorlog.StreamHandler = colorlog.StreamHandler()
    # # Set the formatter for the console handler
    handler.setFormatter(
        colorlog.ColoredFormatter(
            # https://docs.python.org/3/library/logging.html#logging.Formatter
            "%(asctime)s %(log_color)s[%(levelname)-8s] %(reset)s %(white)s %(message)s",
            datefmt = None,
            reset = True,
            log_colors = {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors = {},
            style = '%'
        )
    )

    # Add the console handler to the logger
    logger.addHandler( handler )
    return logger


def get_level_name( n: str ) -> int:
    # https://docs.python.org/3/library/logging.html#logging.getLevelName
    return logging.getLevelName( n.upper() )
