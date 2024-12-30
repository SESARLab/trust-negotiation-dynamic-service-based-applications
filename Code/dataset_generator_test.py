#!/bin/python3

from dataset_generator import generateTrustData, generateRequirement, generatePolicy, generateNumberOfChangingServices, generateChangingServices, generateNumberOfChangingSds, generateChangingSds, generateChange, generateService
import pytest
import const

# TEST FOR generateTrustData FUNCTION
@pytest.mark.parametrize("p", const.SD_PROBABILITIES)
def test_generateTrustData(p):
    """
        To test generateTrustData check if the generated value is in the range of accepted values
    """

    td = generateTrustData(p) 
    assert td[0] in [0, 1, 2]
    assert td[1] in [True, False]

# TEST FOR generateRequirement FUNCTION 
# create parameters list
genReqParams = []

for req_p in const.REQUIREMENT_PROBABILITIES:
    genReqParams.append((req_p['REQUIREMENTS'], req_p['CARDINALITY']))

# test function
@pytest.mark.parametrize("val_p, card_p", genReqParams)
def test_generateRequirement(val_p, card_p):
    """
        To test generateRequirement, check if generated range and cardinality have accepted values 
    """
    
    req = generateRequirement(val_p, card_p)
    
    assert req[0][0] in [0, 1, 2]
    assert req[0][1] == 2
    assert req[1] in [0, 1]
    assert req[2] in [True, False]

# TEST FOR generatePolicy FUNCTION
# create parameters list
genPolParams = []

for pol_p in const.REQUIREMENT_PROBABILITIES:
    genPolParams.append(pol_p['POLICY'])

# test function
@pytest.mark.parametrize("p", genPolParams)
def test_generatePolicy(p):
    """
        To test generatePolicy check if the first value is in accepted range, and if the second value has an accepted value according to the first one 
    """
    
    policy = generatePolicy(p)

    assert policy[0] in [0.3, 0.6]

    if policy[0] == 0.3:
        assert policy[1] == 0.6
    elif policy[1] == 0.6:
        assert policy[1] == 0.9

# TEST FOR generateNumberOfChangingServices FUNCTION
# create parameters list

genChNumParams = []

for n in range(50, 80):
    genChNumParams.append((n, [0.5, 0.5]))

@pytest.mark.parametrize("service_num, probabilities", genChNumParams)
def test_generateNumberOfChangingServices(service_num, probabilities):
    changesNum = generateNumberOfChangingServices(service_num, probabilities)

    assert changesNum >= 0 
    assert changesNum <= 100

# TEST FOR generateChangingServices FUNCTION
# create parameters list
genChNParams = []

for ch_num in range(1, 6): 
    for service_num in range(5, 10):
        if ch_num <= service_num:
            genChNParams.append((service_num, ch_num))   

# test function
@pytest.mark.parametrize("service_n, ch_n", genChNParams)
def test_generateChangingServices(service_n, ch_n):
    """
        To test generateChangingServices check 
        that the generated number of changing services is equal to the change number we want, 
        that the number of changing services is <= of the total number of services, and that all values are unique, so there is not a service with more associated changes 
        We test it with n services in the range [5, 6, 7, 8, 9], 
        and different change number in range [1, 2, 3, 4, 5]
    """

    service_list = generateChangingServices(service_n, ch_n)

    assert len(service_list) == ch_n
    assert len(service_list) <= service_n

    for n in service_list:
        tmpList = service_list.remove(n)

        if tmpList is not None:
            assert n not in tmpList

# TEST FOR generateNumberOfChangingSds FUNCTION
# create parameters list 
genSdNumParams = []

for n in range(50, 80):
    genSdNumParams.append((n, [0.5, 0.5]))

@pytest.mark.parametrize("sds_num, probabilities", genSdNumParams)
def test_generateNumberOfChangingSds(sds_num, probabilities):
    changesNum = generateNumberOfChangingSds(sds_num, probabilities)

    assert changesNum >= 0 
    assert changesNum <= 100

# TEST FOR generateChangingSds FUNCTION
# create parameters list 
genSdChParams = []

for ch_num in range(1, 6): 
    for sds_num in range(5, 10):
        if ch_num <= sds_num:
            genSdChParams.append((sds_num, ch_num))   

@pytest.mark.parametrize("sds_num, change_num", genSdChParams)
def test_generateChangingSds(sds_num, change_num):
    sdList = generateChangingSds(sds_num, change_num)

    assert len(sdList) <= sds_num
    assert len(sdList) == change_num

    for n in sdList:
        tmpList = sdList.remove(n)

        if tmpList is not None:
            assert n not in tmpList

# TEST FOR generateChange FUNCTION
# create parameters list 

genChParams = (
    {
        'name': 'testService',
        'sd0': (1, True), 
        'req0': (2, 1, True),
        'sd1': (0, False),
        'req1': (1, 0, False),
        'policy': [0.3, 0.6]
    },
    [0, 1]
)

# test function
@pytest.mark.parametrize("service, changingSd", [genChParams])
def test_generateChange(service, changingSd):
    """
        To test generateChange check that the value of the new sd is different from the old value and the new value is in the range of accepted value [0, 1, 2]
    """

    change = generateChange(service, changingSd)

    assert len(change) <= len(changingSd)

    for i in range(len(change)):
        assert change[i][1] != service[f'sd{i}']
        assert change[i][1] >= 0
        assert change[i][1] <= 2 

# TEST FOR generateService FUNCTION
# create parameters list 
genServParams = (
    0,
    1,
    const.SD_PROBABILITIES[0],
    const.REQUIREMENT_PROBABILITIES[0]['REQUIREMENTS'],
    const.REQUIREMENT_PROBABILITIES[0]['CARDINALITY'],
    const.REQUIREMENT_PROBABILITIES[0]['POLICY']
)

@pytest.mark.parametrize("index, sds_num, sd_probabilities, r_val_probabilities, r_card_probabilities, r_pol_probabilities", [genServParams])
def test_generateService(index, sds_num, sd_probabilities, r_val_probabilities, r_card_probabilities, r_pol_probabilities):
    service = generateService(index, sds_num, sd_probabilities, r_val_probabilities, r_card_probabilities, r_pol_probabilities)

    for i in range(sds_num):
        assert f'sd{i}' in service
        assert f'req{i}' in service
    
    assert 'name' in service
    assert 'policy' in service
