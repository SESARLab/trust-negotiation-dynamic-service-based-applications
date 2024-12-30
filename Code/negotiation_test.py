#!/bin/python3

from negotiation import match, matching, negotiation, analysis, planning, execution, dynamicTrust
from dataset_generator import generateTrustData, generateRequirement, generatePolicy, generateService, generateChange
import pytest
import const

# TEST FOR match FUNCTION 
# create parameters list 
matchParams = []

for i in range(5):
    matchParams.append((generateTrustData(const.SD_PROBABILITIES[0]), generateRequirement(const.REQUIREMENT_PROBABILITIES[0]['REQUIREMENTS'], const.REQUIREMENT_PROBABILITIES[0]['CARDINALITY'])[0], True))


# test function 
@pytest.mark.parametrize("sd, r, c", matchParams)
def test_match(sd, r, c):
    """
        To test match check if the result is a boolean value 
    """
    
    assert match(sd, r, c) in [True, False]


# TEST FOR matching FUNCTION 
# create parameters list 
matchingParams = []

for i in range(5):
    matchingParams.append(([[generateTrustData(const.SD_PROBABILITIES[0])]], [generateRequirement(const.REQUIREMENT_PROBABILITIES[0]['REQUIREMENTS'], const.REQUIREMENT_PROBABILITIES[0]['CARDINALITY'])]))


# test function
@pytest.mark.parametrize("sds, req", matchingParams)
def test_matching(sds, req):
    """
        To test matching check that the retrieved satisfaction is in the interval [0, 1]
    """
    
    sat = matching(sds, req)
    assert sat <= 1 and sat >= 0 


# TEST FOR negotiation FUNCTION 
# create parameters list 
negotiationParams = []

for i in range(5):
    services = []

    for j in range(5):
        s = generateService(j, 5, const.SD_PROBABILITIES[0], const.REQUIREMENT_PROBABILITIES[0]['REQUIREMENTS'], const.REQUIREMENT_PROBABILITIES[0]['CARDINALITY'], const.REQUIREMENT_PROBABILITIES[0]['POLICY'])

        services.append(s)
    
    negotiationParams.append(services)


# test function 
@pytest.mark.parametrize("services_", negotiationParams)
def test_negotiation(services_):
    """
        To test negotiation check that: 
         - Every entry of the resulting list have 2 values (the service and its satisfaction degree) 
         - The satisfaction of every service is in the interval [0, 1]
         - the returned service is a dict
         - the number of services that join the system must be at least 1 and no bigger than the services that made a request
    """
    
    system = negotiation(services_)

    for n in system: 
        assert len(n) == 2
        assert 0 <= n[1] <= 1
        assert isinstance(n[0], dict) 

    assert 0 <= len(system) <= len(services)


# TEST FOR analysis FUNCTION 
# create parameters list 
analysisParams = []

for i in range(5):
    services = []

    for j in range(5):
        s = generateService(j, 5, const.SD_PROBABILITIES[0], const.REQUIREMENT_PROBABILITIES[0]['REQUIREMENTS'], const.REQUIREMENT_PROBABILITIES[0]['CARDINALITY'], const.REQUIREMENT_PROBABILITIES[0]['POLICY'])

        s['change'] = generateChange(s, [1])

        services.append([s, 0.6])
    
    analysisParams.append((services[0], services))


@pytest.mark.parametrize("service, services_", analysisParams)
def test_analysis(service, services_):
    res = analysis(service, services_)

    assert res[0] is True or res[0] is False


@pytest.mark.parametrize("service, services_", analysisParams)
def test_planning(service, services_):
    res = planning(service, services_)

    assert res is True or res is False


@pytest.mark.parametrize("service, services_", analysisParams)
def test_execution(service, services_):
    old_l = len(services_)

    res = execution(True, service, services_)

    assert len(services) > 0
    assert len(services) <= old_l


# TEST FOR dynamicTrust FUNCTION 
# create parameters list 
dynamicTrustParams = []

for i in range(5):
    services = []

    for j in range(5):
        s = generateService(j, 5, const.SD_PROBABILITIES[0], const.REQUIREMENT_PROBABILITIES[0]['REQUIREMENTS'], const.REQUIREMENT_PROBABILITIES[0]['CARDINALITY'], const.REQUIREMENT_PROBABILITIES[0]['POLICY'])

        s['change'] = generateChange(s, [1])

        services.append([s, 0.6])
    
    dynamicTrustParams.append(services)


# test function 
@pytest.mark.parametrize("system", dynamicTrustParams)
def test_dynamicTrust(system):
    """
        To test dynamicTrust check that: 
         - Every entry of the resulting list have 2 values (the service and its satisfaction degree) 
         - The satisfaction of every service is in the interval bigger than the lowest value of its policy 
         - the returned service is a dict
         - the number of services in the system is equal or minor of the number of services before the change 
    """

    lenSys = len(system)

    upd_system = dynamicTrust(system)

    assert len(upd_system) <= lenSys

    for n in upd_system[1]: 
        assert n[1] >= n[0]['policy'][0]