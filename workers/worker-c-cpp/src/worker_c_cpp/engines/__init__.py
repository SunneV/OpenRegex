from openregex_libs.models import WorkerInfo, WORKER_SCHEMA_VERSION
from .common import WORKER_VERSION, WORKER_RELEASE_DATE
from .cpp_re2 import engine as cpp_re2
from .cpp_std import engine as cpp_std
from .cpp_boost import engine as cpp_boost
from .c_posix import engine as c_posix
from .c_pcre2 import engine as c_pcre2
from .c_onig import engine as c_onig
from .cpp_hyperscan import engine as cpp_hyperscan

ENGINES = [
    cpp_re2,
    cpp_std,
    cpp_boost,
    c_posix,
    c_pcre2,
    c_onig,
    cpp_hyperscan
]

WORKER_INFO = WorkerInfo(
    worker_name="worker-c-cpp",
    worker_version=WORKER_VERSION,
    worker_release_date=WORKER_RELEASE_DATE,
    worker_schema_version=WORKER_SCHEMA_VERSION,
    engines=ENGINES
)