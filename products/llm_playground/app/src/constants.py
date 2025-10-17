# Any constants go here
import os
from enum import Enum
from pathlib import Path

LICENSE_PATH = "license.json"
if not os.path.isfile(LICENSE_PATH):
    LICENSE_PATH = "/app/secret/license.json"
    if not os.path.isfile(LICENSE_PATH):
        raise Exception(f"License file not found!")

PROP_PATH = "/opt/.prop"
BUCKET = "auxdata.johnsnowlabs.com"
LLM_S3_KEY = "clinical/models/non-spark-models/llms"
LLM_MAP_S3_KEY = f"{LLM_S3_KEY}/llms_map.json"
NO_DEPLOYED_MODEL_MSG = (
    "No model loaded. Use POST '/deploy' to load or GET '/status' to check."
)


class Status(Enum):
    STARTING = "starting"
    DEPLOYING = "deploying"
    FINALIZING = "finalizing"
    DEPLOYED = "deployed"
    FAILED = "failed"

    EMPTY_RESULT = "no result found"
    LLM_NOT_FOUND = "this llm not ready/available"

    JOB_IN_PROGRESS = (
        "a deployment is in progress. check `GET /status` and try again in a moment"
    )
    DEPLOYMENT_STARTED = "deployment started"


BUSY_STATUS = [Status.STARTING.value, Status.DEPLOYING.value, Status.FINALIZING.value]
