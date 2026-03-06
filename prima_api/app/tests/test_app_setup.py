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

# Standard libs
import logging

# Installed libs
import pytest

# User-defined libs
from app_setup import setup_logger


def test_setup_logger(tmp_path, caplog):
    """
    Checks for the setup_logger method
    """
    caplog.set_level(logging.DEBUG)

    # Catch exception on incorrect log level
    log_file = tmp_path / "temp.log"
    with pytest.raises(ValueError):
        setup_logger(log_level=10, log_file=log_file)

    # Check correct execution
    setup_logger(log_level=3, log_file=log_file)
    logger = logging.getLogger("test")
    logger.info("This is a test!")
    assert "This is a test!" in caplog.text
