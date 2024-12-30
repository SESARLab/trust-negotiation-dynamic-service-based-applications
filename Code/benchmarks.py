#!/bin/python3

import pytest
import random
from negotiation import negotiation, dynamicTrust, analysis, planning, execution
from dataset_reader import getServicesFromDataset


@pytest.mark.benchmark(
    group = "negotiation",
    min_rounds = 5,
    disable_gc = True,
    warmup = False
)

def test_negotiation(benchmark, request):
    services = getServicesFromDataset(f"{request.config.getoption('--path')}/datasets/execution1/dataset_{request.config.getoption('--setting')}.csv")

    benchmark(negotiation, services)

@pytest.mark.benchmark(
    group = "dynamic_trust",
    min_rounds = 5,
    disable_gc = True,
    warmup = False
)

def test_dynamicTrust(benchmark, request):
    system = negotiation(getServicesFromDataset(f"{request.config.getoption('--path')}/datasets/execution1/dataset_{request.config.getoption('--setting')}.csv"))

    benchmark(dynamicTrust, system)


@pytest.mark.benchmark(
    group = "analysis",
    min_rounds = 5,
    disable_gc = True,
    warmup = False
)

def test_analysis(benchmark, request):
    services = negotiation(getServicesFromDataset(f"{request.config.getoption('--path')}/datasets/execution1/dataset_{request.config.getoption('--setting')}.csv"))
    
    tmp = None

    for n in services:
        if n[0]['change'] != (None, None):
            tmp = n
            break

    if tmp is None:
        services[0][0]['change'] != ('sd0', 1)
        tmp = services[0]
    
    benchmark(analysis, tmp, services)

@pytest.mark.benchmark(
    group = "planning",
    min_rounds = 5,
    disable_gc = True,
    warmup = False
)

def test_planning(benchmark, request): 
    services = negotiation(getServicesFromDataset(f"{request.config.getoption('--path')}/datasets/execution1/dataset_{request.config.getoption('--setting')}.csv"))

    benchmark(planning, services[0], services)

@pytest.mark.benchmark(
    group = "execution",
    min_rounds = 5,
    disable_gc = True,
    warmup = False
)

def test_execution(benchmark, request): 
    services = negotiation(getServicesFromDataset(f"{request.config.getoption('--path')}/datasets/execution1/dataset_{request.config.getoption('--setting')}.csv"))

    benchmark(execution, bool(random.getrandbits(1)), services[0], services)