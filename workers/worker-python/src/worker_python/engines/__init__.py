from openregex_libs.models import WorkerInfo, WORKER_SCHEMA_VERSION
from .common import WORKER_VERSION, WORKER_RELEASE_DATE
from .python_re import engine as python_re
from .python_regex import engine as python_regex

ENGINES = [
    python_re,
    python_regex
]

WORKER_INFO = WorkerInfo(
    worker_name="worker-python",
    worker_version=WORKER_VERSION,
    worker_release_date=WORKER_RELEASE_DATE,
    worker_schema_version=WORKER_SCHEMA_VERSION,
    engines=ENGINES
)