import logging

import pytest

from project import log
from src.engine.cpp.cpp import _REGEX_EXAMPLES_PYTHON_CPP as REGEX_EXAMPLES_PYTHON_CPP
from src.engine.java.java import _REGEX_EXAMPLES_PYTHON_JAVA as REGEX_EXAMPLES_PYTHON_JAVA
from src.engine.python_re import _REGEX_EXAMPLES_PYTHON_RE as REGEX_EXAMPLES_PYTHON_RE
from src.engine.python_regex import _REGEX_EXAMPLES_PYTHON_REGEX as REGEX_EXAMPLES_PYTHON_REGEX
from src.utils.link import decode_dict, encode_dict


@pytest.fixture(scope="session", autouse=True)
def set_log_level():
    log.setLevel(logging.DEBUG)


class TestZip85:
    def test_encode_decode(self):
        data = {"e": "Python - regex", "r": r"(?P<name>\w+)", "t": "Hello, World!"}

        encoded_data = encode_dict(data)
        decode_data = decode_dict(encoded_data)

        log.info(f"Input Data: {data}")
        log.info(f"Encoded Data: {encoded_data}")
        log.info(f"Decoded Data: {decode_data}")
        assert data == decode_data

    def test_big_data(self):
        data_list = [
            REGEX_EXAMPLES_PYTHON_RE,
            REGEX_EXAMPLES_PYTHON_REGEX,
            REGEX_EXAMPLES_PYTHON_CPP,
            REGEX_EXAMPLES_PYTHON_JAVA,
        ]

        data_to_check = []
        for data in data_list:
            encoded_data = encode_dict(data)
            decode_data = decode_dict(encoded_data)
            data_to_check.append((encoded_data, decode_data))

        for data, (encoded_data, decoded_data) in zip(data_list, data_to_check):  # Correct unpacking
            log.info(f"Encoded Data: {encoded_data}")
            log.info(f"Decoded Data: {decoded_data}")
            assert data == decoded_data
