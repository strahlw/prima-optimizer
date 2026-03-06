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
Implements a basic Celery based background tasks manager for running PRIMO instances, 
querying their status and/or terminating them when needed
"""
# Standard libs
import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler

# Installed libs
import redis
from celery import Celery, signals
from celery.exceptions import Ignore
from celery.result import AsyncResult
from pymongo import MongoClient

# User-defined libs
from app_setup import setup_logger
from parameters import (
    LOGGER_DATE,
    LOGGER_FORMAT,
    MONGO_URI,
    REDIS_BACKEND_URL,
    REDIS_BROKER_URL,
    REDIS_HOST,
    REDIS_PORT,
)
from primo_executor.primo_worker import (
    infer_use_case_type,
    solve_primo_model,
    solve_primo_model_override,
)
from utils.models import ManualOverrideRequest, ScenarioParameters, Status
from utils.raise_exception import raise_exception

LOGGER = logging.getLogger(__name__)

JOBS_KEYS = {
    "ALL": "PRIMO-API:JOBS",
    "PENDING": "PRIMO-API:JOBS:PENDING",
    "PROCESSING": "PRIMO-API:JOBS:PROCESSING",
    "RETRY": "PRIMO-API:JOBS:RETRY",
    "FAILURE": "PRIMO-API:JOBS:FAILURE",
    "SUCCESS": "PRIMO-API:JOBS:SUCCESS",
}


FINISHED_SET = "PRIMO-API:JOBS"


@signals.after_setup_logger.connect
@signals.after_setup_task_logger.connect
def setup_custom_logger(logger, *args, **kwargs):  # pylint: disable=unused-argument
    """
    Set up custom logging for celery workers
    """
    handlers = []
    stdout_handler = logging.StreamHandler(sys.stdout)
    handlers.append(stdout_handler)
    formatter = logging.Formatter(LOGGER_FORMAT, LOGGER_DATE)
    file_handler = RotatingFileHandler(
        "logs/celery.log", maxBytes=2000000, backupCount=10
    )
    handlers.append(file_handler)

    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)


class Queue(Celery):
    """
    Modifies Celery to include a Redis connection object and a mechanism
    for keeping track of Job statuses after they are completed. Assumes the
    broker and backend connections utilized are Redis connections

    Parameters
    ----------
    redis_host : str
        The connection string for the Redis host

    redis_port : int
        The port at which redis is being served

    redis_db : int
        The database to connect to
    """

    def __init__(
        self,
        redis_host: str,
        redis_port: int = None,
        redis_db: int = 0,
        **kwargs,
    ):
        super().__init__(**kwargs)
        setup_logger()
        self._redis_pool = redis.ConnectionPool(
            host=redis_host, port=redis_port, db=redis_db
        )
        # Test if connection is valid
        try:
            redis_obj = self.get_redis_connection()
            redis_obj.ping()
        except redis.exceptions.ConnectionError:
            msg = "Could not connect to the Redis database. Please check credentials"
            raise_exception(msg, ValueError)
        LOGGER.debug("Initialized Redis Connection Pool")

    def get_redis_connection(self):
        """
        Get a connection object from the pool initialized within the object
        """
        return redis.StrictRedis(connection_pool=self._redis_pool)

    def is_valid_job_id(self, task_id: str) -> bool:
        """
        Returns if a task_id is valid, i.e. if the job id was created
        by a previous run_primo_instance call
        """
        LOGGER.debug(f"Checking if task_id: {task_id} is valid")
        redis_obj = self.get_redis_connection()
        return redis_obj.sismember(JOBS_KEYS["ALL"], task_id)


QUEUE_APP = Queue(
    redis_host=REDIS_HOST,
    redis_port=REDIS_PORT,
    redis_db=0,
    main=__name__,
    broker=REDIS_BROKER_URL,
    backend=REDIS_BACKEND_URL,
)
QUEUE_APP.conf.task_track_started = True
QUEUE_APP.conf.broker_connection_retry_on_startup = True


@QUEUE_APP.task(name="run_primo", bind=True)
def run_primo_instance(
    self,
    parameters,
    override: bool | None = False,
):
    """
    Runs primo job with user defined parameters

    Parameters
    ----------
    parameters
        Global configuration parameters related to running a PRIMO job

    override: bool
        Whether the PRIMO job is executed in a reoptimization scenario

    Returns
    -------
    None
    """
    LOGGER.info("Running run primo instance!")
    task_id = self.request.id
    redis_obj = QUEUE_APP.get_redis_connection()
    # Remove job from pending status and add to processing status
    redis_obj.srem(JOBS_KEYS["PENDING"], task_id)
    redis_obj.sadd(JOBS_KEYS["PROCESSING"], task_id)
    if override:
        scenario_parameters = ManualOverrideRequest.model_validate(parameters)
    else:
        scenario_parameters = ScenarioParameters.model_validate(parameters)

    scenario_type = infer_use_case_type(scenario_parameters)

    try:
        if override:
            solve_primo_model_override(
                scenario_parameters.general_specifications,
                scenario_parameters.child_scenario_id,
                scenario_parameters,
                scenario_type,
            )
        else:
            solve_primo_model(scenario_parameters)
    except Exception as exc:
        description = str(exc)
        self.update_state(
            state=Status.FAILURE,
            meta={
                "status": description,
                "exc_type": "ValueError",
                "exc_message": traceback.format_exc(),
            },
        )
        redis_obj.sadd(JOBS_KEYS["FAILURE"], task_id)
        redis_obj.srem(JOBS_KEYS["PROCESSING"], task_id)
        raise Ignore() from exc

    # TODO: Document failure modes and set up checks for it
    redis_obj.sadd(JOBS_KEYS["SUCCESS"], task_id)
    redis_obj.srem(JOBS_KEYS["PROCESSING"], task_id)

    with MongoClient(MONGO_URI) as client:
        client.server_info()

    # Off chance that the task id got added to the pending queue
    # after it started executing
    redis_obj.srem(JOBS_KEYS["PENDING"], task_id)


def add_job_to_queue(task_id: str):
    """
    Adds a job id to the queue in pending status so it is
    correctly tracked

    Parameters
    ----------
    task_id : str
        Task id for the task to be added to the queue
    """
    redis_obj = QUEUE_APP.get_redis_connection()
    redis_obj.sadd(JOBS_KEYS["ALL"], task_id)
    redis_obj.sadd(JOBS_KEYS["PENDING"], task_id)


def get_primo_job_status(task_id: str) -> AsyncResult:
    """
    Gets the job status for a primo job as an AsyncResult object
    (https://docs.celeryq.dev/en/stable/reference/celery.result.html)

    Parameters
    ----------
    task_id : str
        The task whose status is to be queried

    Returns
    -------
    AsyncResult
        AsyncResult object (from Celery Package) with the status of the job
    """
    return QUEUE_APP.AsyncResult(task_id)


def kill_primo_job(task_id: str) -> None:
    """
    Kills a job identified by task_id

    Parameters
    ----------
    task_id : str
        The task to be killed

    Returns
    -------
    None
    """
    LOGGER.info(f"Kill primo task id : {task_id}")
    QUEUE_APP.control.revoke(task_id, terminate=True, signal="SIGKILL")
