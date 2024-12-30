#!/bin/python3

import pytest

def pytest_addoption(parser):
    parser.addoption("--setting", action = "store", default = "None")
    parser.addoption("--path", action = "store", default = "None")
