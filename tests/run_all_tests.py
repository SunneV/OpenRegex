import logging

import pytest

from project import log


@pytest.fixture(scope="session", autouse=True)
def set_log_level():
    log.setLevel(logging.DEBUG)


if __name__ == "__main__":
    # Discover and run all test
    pytest.main([".", "--junitxml=report/report.xml", "--html=report/report.html"])
