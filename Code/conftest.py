#!/bin/python3

import pytest

def pytest_addoption(parser):
    parser.addoption('--dataset-dir', action='store', default=None)
