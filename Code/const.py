#!/bin/python3

# EXECUTIONS VALUES

# ADVICE FOR TESTING: 
#  - leave EXECUTION = 10  
#  - SERVICES_NUM = [10]
#  - SDS_NUM = [10]
#  - CHS_NUM = [1] 
# not meaningful but fast to check results format

EXECUTION = 5
SERVICES_NUM = [10, 25, 50, 100]
SDS_NUM = [10, 25, 50, 100]

# VALUES 
# service data values
SD_VALUE = {
    'BAD': 0,
    'AVG': 1,
    'GOOD': 2
}

REQ_CARDINALITY_EXISTS = 0
REQ_CARDINALITY_FORALL = 1

# cardinalities values
REQ_CARDINALITY = {
    'EXISTS': REQ_CARDINALITY_EXISTS,
    'FORALL': REQ_CARDINALITY_FORALL
}

# policies values
POLICIES = {
    'LOOSE': [0.3, 0.6],
    'STRICT': [0.6, 0.9]
}

# change worsening 
CHANGE = {
    'WORSENING': 0, 
    'IMPROVING': 1
}

# PROBABILITIES
# service data probabilities
SD_PROBABILITIES = [
    [1/3, 1/3, 1/3],
    [0.5, 0.25, 0.25],
    [0.25, 0.5, 0.25],
    [0.25, 0.25, 0.5],
]

# policies and requirements probabilities 
REQUIREMENT_PROBABILITIES = [
    {
        'POLICY': [0.5, 0.5],
        'REQUIREMENTS': [1/3, 1/3, 1/3],
        'CARDINALITY': [0.5, 0.5]
    },
    {
        'POLICY': [2/3, 1 - 2/3],
        'REQUIREMENTS': [2/3, (1/3) / 2, (1/3) / 2],
        'CARDINALITY': [2/3, 1/3]
    },
    {
        'POLICY': [2/3, 1 - 2/3],
        'REQUIREMENTS': [(1/3) / 2, 2/3, (1/3) / 2],
        'CARDINALITY': [2/3, 1/3] 
    }
]

# changes
CHANGES_PROBABILITIES = [
    {
        'SERVICE': [0.25, 1 - 0.25],
        'DATA': [0.25, 1 - 0.25]
    },
    {
        'SERVICE': [0.25, 1 - 0.25],
        'DATA': [0.75, 1 - 0.75]
    },
    {
        'SERVICE': [0.75, 1 - 0.75],
        'DATA': [0.25, 1 - 0.25]
    }
]

# SETTINGS
def getSettings():
    SETTINGS = []
    sd_i = 0

    for sd_p in SD_PROBABILITIES:
        req_i = 0
        for req_p in REQUIREMENT_PROBABILITIES:
            ch_i = 0
            for ch_p in CHANGES_PROBABILITIES: 
                SETTINGS.append({
                    'SETTING_NAME': f'G{sd_i + 1}.{req_i + 1}.{ch_i + 1}',
                    'SD_P': sd_p, 
                    'REQS_P': req_p,
                    'CH_P': ch_p           
                })

                ch_i += 1
            req_i += 1
        sd_i += 1

    return SETTINGS
