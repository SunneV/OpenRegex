import pytest

from project import log

log.setLevel("DEBUG")

if __name__ == "__main__":
    # Discover and run all test
    pytest.main([".", "--junitxml=report/report.xml", "--html=report/report.html"])
