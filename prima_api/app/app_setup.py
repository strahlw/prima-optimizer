#################################################################################
# PRIMO - The P&A Project Optimizer was produced under the Methane Emissions
# Reduction Program (MERP) and National Energy Technology Laboratory's (NETL)
# National Emissions Reduction Initiative (NEMRI).
#
# NOTICE. This Software was developed under funding from the U.S. Government
# and the U.S. Government consequently retains certain rights. As such, the
# U.S. Government has been granted for itself and others acting on its behalf
# a paid-up, nonexclusive, irrevocable, worldwide license in the Software to
# reproduce, distribute copies to the public, prepare derivative works, and
# perform publicly and display publicly, and to permit others to do so.
#################################################################################
"""
Initializes the app using FastAPI
"""

# Standard libs
import logging
import sys
from logging.handlers import RotatingFileHandler
from typing import Tuple

# Installed libs
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

# User-defined libs
from parameters import (
    ALLOWED_HOSTS,
    API_LOGFILE,
    BACKUP_COUNT,
    FAVICON_URL,
    LOGGER_DATE,
    LOGGER_FORMAT,
    LOGO_URL,
    MAX_BYTES,
    VERSION,
)
from utils.raise_exception import raise_exception


def setup_logger(
    log_level: int = 3,
    log_to_console: bool = True,
    log_file: str = API_LOGFILE,
    max_bytes: int = MAX_BYTES,
    backup_count: int = BACKUP_COUNT,
):
    """
    Sets up logging objects based on user input. The log_file if specified is set
    up as a RotatingFileHandler

    Parameters
    ----------
    log_level : int, default = 3
        The level of logging messages---0: off; 1: warning; 2: info; 3: debug;

    log_to_console : bool, default = True
        If True, log messages are displayed on the screen in addition
        to the log file (if configured)

    log_file : str, default = None
        The path on the disk where log files are written

    max_bytes : int, default = 2000000
        The maximum size a log file is allowed to reach before being rotated (in bytes)

    backup_count : int, default = 10
        The maximum number of rotating files kept in logs

    Returns
    -------
    logging.Logger
        A logger object set up as required

    Raises
    ------
    ValueError
        If the log_file specified already exists or if an invalid value for
        log_level is provided
    """
    supported_log_levels = {
        0: logging.CRITICAL,
        1: logging.WARNING,
        2: logging.INFO,
        3: logging.DEBUG,
    }
    if log_level not in supported_log_levels:
        raise_exception(
            f"Invalid value for log_level: {log_level}. Acceptable values are: [0, 1, 2, 3]",
            ValueError,
        )

    handlers = []
    if log_to_console:
        stdout_handler = logging.StreamHandler(sys.stdout)
        handlers.append(stdout_handler)

    if log_file is not None:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        handlers.append(file_handler)

    logging.basicConfig(
        level=supported_log_levels[log_level],
        format=LOGGER_FORMAT,
        datefmt=LOGGER_DATE,
        handlers=handlers,
    )


def initialize_app() -> Tuple[FastAPI, HTMLResponse, HTMLResponse]:
    """
    Initializes the FastAPI object
    """
    app = FastAPI(docs_url=None, redoc_url=None)

    document_api(app)

    # Ensure only specified hosts can query the API
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)

    # Ensure the favicon is displayed correctly
    swagger_ui_html = get_swagger_ui_html(
        openapi_url="/openapi.json", title="PRIMO-API", swagger_favicon_url=FAVICON_URL
    )

    redoc_ui_html = get_redoc_html(
        openapi_url="/openapi.json", title="PRIMO-API", redoc_favicon_url=FAVICON_URL
    )

    # Set up logger!
    setup_logger()
    return app, swagger_ui_html, redoc_ui_html


def document_api(app: FastAPI):
    """
    Add documentation for the API App such as title, description, license, contact information
    and logo
    """

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title="PRIMO-API",
            version=VERSION,
            summary="PRIMO as an API",
            description=(
                "This project wraps up [PRIMO](https://primo.readthedocs.io/en/latest/) "
                "in an API layer built using "
                "[FastAPI](https://fastapi.tiangolo.com/), "
                "[Celery](https://docs.celeryq.dev/en/stable/getting-started/introduction.html),"
                " and [Docker](https://www.docker.com/). This makes it possible to use PRIMO as "
                " an API service in your application of choice."
            ),
            routes=app.routes,
            contact={
                "name": "The PRIMO team",
                "url": "https://primo.readthedocs.io/en/latest/",
                "email": "primo@netl.doe.gov",
            },
            license_info={
                "name": "BSD 3-Clause Clear License",
                "identifier": "BSD-3-Clause-Clear",
                "url": "https://github.com/NEMRI-org/primo-optimizer/blob/main/LICENSE.md",
            },
        )

        # Update to use PRIMO logo
        openapi_schema["info"]["x-logo"] = {"url": LOGO_URL}
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
