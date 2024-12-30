#!/bin/python3

import pytest
import os
from dataset_reader import getServicesFromDataset, getSdsFromService, getReqsFromService
from dataset_generator import DatasetGenerator

# TEST FOR getServicesFromDataset FUNCTION 
# create parameters list
getServicesFromDatasetParams = []

setting = [{'SETTING_NAME': 'G0.0.0', 'SD_P': [0.3333333333333333, 0.3333333333333333, 0.3333333333333333], 'REQS_P': {'POLICY': [0.5, 0.5], 'REQUIREMENTS': [0.3333333333333333, 0.3333333333333333, 0.3333333333333333], 'CARDINALITY': [0.5, 0.5]}, 'CH_P': {'TYPE': [0.5, 0.5], 'CHANGE': [0.3333333333333333, 0.3333333333333333, 0.3333333333333333]}}, {'SETTING_NAME': 'G0.0.1', 'SD_P': [0.3333333333333333, 0.3333333333333333, 0.3333333333333333], 'REQS_P': {'POLICY': [0.5, 0.5], 'REQUIREMENTS': [0.3333333333333333, 0.3333333333333333, 0.3333333333333333], 'CARDINALITY': [0.5, 0.5]}, 'CH_P': {'TYPE': [0.6666666666666666, 0.33333333333333337], 'CHANGE': [0.3333333333333333, 0.3333333333333333, 0.3333333333333333]}}, {'SETTING_NAME': 'G0.0.2', 'SD_P': [0.3333333333333333, 0.3333333333333333, 0.3333333333333333], 'REQS_P': {'POLICY': [0.5, 0.5], 'REQUIREMENTS': [0.3333333333333333, 0.3333333333333333, 0.3333333333333333], 'CARDINALITY': [0.5, 0.5]}, 'CH_P': {'TYPE': [0.3333333333333333, 0.6666666666666667], 'CHANGE': [0.3333333333333333, 0.3333333333333333, 0.3333333333333333]}}]

for s in setting:
    DatasetGenerator(s).generate(10, 10, f".test_dataset{s['SETTING_NAME']}.csv")
    getServicesFromDatasetParams.append(f".test_dataset{s['SETTING_NAME']}.csv")

# test function
@pytest.mark.parametrize("f", getServicesFromDatasetParams)
def test_getServicesFromDataset(f):
    services = getServicesFromDataset(f)
    
    assert len(services) > 0

    for n in services: 
        assert isinstance(n, dict)

# TEST FOR getSdsFromService FUNCTION 
# create parameters list 
getSdsFromServiceParams = []
sdsNum = 5
sdsVal = 0

for i in range(5):
    service = {}

    for j in range(sdsNum):
        service[f'sd{j}'] = sdsVal
        
    getSdsFromServiceParams.append(service)

# test function 
@pytest.mark.parametrize("service", getSdsFromServiceParams)
def test_getSdsFromService(service):
    sds = getSdsFromService(service)

    assert len(sds) == sdsNum
    
    for t in sds:
        assert t == sdsVal

# TEST FOR getReqsFromService FUNCTION 
# create parameters list 
getReqsFromServiceParams = []
reqsNum = 5
reqsVal = [0, 2]
cardVal = 1

for i in range(5):
    service = {}

    for j in range(sdsNum):
        service[f'req{j}'] = (reqsVal, cardVal)
        
    getReqsFromServiceParams.append(service)

# test function 
@pytest.mark.parametrize("service", getReqsFromServiceParams)
def test_getReqsFromService(service):
    sds = getReqsFromService(service)

    assert len(sds) == reqsNum
    
    for t in sds:
        assert t[0][0] == reqsVal[0]
        assert t[0][1] == reqsVal[1]

        assert t[1] == cardVal
