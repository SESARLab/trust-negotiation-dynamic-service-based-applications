#!/usr/bin/python3
import json
import argparse
import sys

import numpy as np

import const
import walkthrough_base

parser = argparse.ArgumentParser()

parser.add_argument('-o', '--output-file', type=str)

args = parser.parse_args()

"""
Define your services in this array, using this format:
{
    'service': 0, # index of service 
    'name': 'service0', # name of the service
    'sd0': (1, True), # value and certificate of the service data 0
    'req0': ([0, 2], 1, True), # range of accepted value, cardinality and certification request for service data 0
    ... add any sd and req you want 
    'policy': [0.3, 0.6], # low threshold and high threshold for actions
}
"""

services = [
    {
      'service': 0,
        'name': 's_brazil',
        'sd0': ('three_biggest_cities', False),  # sample type
        'sd1': (25, False),  # cardinality
        'sd2': ('WEU', False), # location
        'req0': ({'national', 'three_biggest_cities', 'urban'}, const.REQ_CARDINALITY_FORALL, True), # requirement on type
        'req1': ([20, np.inf], const.REQ_CARDINALITY_FORALL, False), # requirement on cardinality
        'req2': ({'WEU', 'LATAM'}, const.REQ_CARDINALITY_EXISTS, False), # requirement on location
        'policy': [0.4, 0.6]
    },
    {
        'service': 1,
        'name': 's_chile',
        'sd0': ('national', False),  # sample type
        'sd1': (25, False),  # cardinality
        'sd2': ('LATAM', False),  # location
        'req0': ({'national', 'three_biggest_cities', 'urban'},
                 const.REQ_CARDINALITY_FORALL, True),  # requirement on type
        'req1': ([1, np.inf], const.REQ_CARDINALITY_FORALL, False),  # requirement on cardinality
        'req2': ({'EEU', 'WEU', 'LATAM'}, const.REQ_CARDINALITY_FORALL, False),  # requirement on location
        'policy': [0.4, 0.7],
        'change': []
    },
    {
        'service': 2,
        'name': 's_france',
        'sd0': ('national', True),  # sample type
        'sd1': (30, True),  # cardinality
        'sd2': ('WEU', True),  # location
        'req0': ({'national'}, const.REQ_CARDINALITY_EXISTS, True),  # requirement on type
        'req1': ([1, np.inf], const.REQ_CARDINALITY_FORALL, False),  # requirement on cardinality
        'req2': ({'WEU', 'EEU'}, const.REQ_CARDINALITY_FORALL, True),  # requirement on location
        'policy': [0.4, 0.7],
        'change': []
    },
    {
        'service': 3,
        'name': 's_italy',
        'sd0': ('national', True),  # sample type
        'sd1': (30, True),  # cardinality
        'sd2': ('WEU', True),  # location
        'req0': ({'national', 'three_biggest_cities', 'urban'},
                 const.REQ_CARDINALITY_FORALL, True),  # requirement on type
        'req1': ([30, np.inf], const.REQ_CARDINALITY_FORALL, False),  # requirement on cardinality
        'req2': ({'EEU', 'WEU'}, const.REQ_CARDINALITY_EXISTS, True),  # requirement on location
        'policy': [1],
        'change': []
    },
    {
        'service': 4,
        'name': 's_mexico',
        'sd0': ('three_biggest_cities', False),  # sample type
        'sd1': (25, False),  # cardinality
        'sd2': ('LATAM', False),  # location
        'req0': ({'national', 'three_biggest_cities', 'urban'},
                 const.REQ_CARDINALITY_FORALL, True),  # requirement on type
        'req1': ([25, np.inf], const.REQ_CARDINALITY_FORALL, False),  # requirement on cardinality
        'req2': ({'LATAM'}, const.REQ_CARDINALITY_EXISTS, False),  # requirement on location
        'policy': [0.2, 0.5],
        'change': []
    },
    {
        'service': 5,
        'name': 's_poland',
        'sd0': ('national', True),  # sample type
        'sd1': (28, True),  # cardinality
        'sd2': ('EEU', True),  # location
        'req0': ({'national', 'three_biggest_cities', 'urban'},
                 const.REQ_CARDINALITY_FORALL, True),  # requirement on type
        'req1': ([1, np.inf], const.REQ_CARDINALITY_FORALL, False),  # requirement on cardinality
        'req2': ({'WEU', 'EEU', 'LATAM'}, const.REQ_CARDINALITY_FORALL, False),  # requirement on location
        'policy': [0.2, 0.5],
        'change': []
    },
    {
        'service': 6,
        'name': 's_romania',
        'sd0': ('national', True),  # sample type
        'sd1': (35, True),  # cardinality
        'sd2': ('EEU', True),  # location
        'req0': ({'national'}, const.REQ_CARDINALITY_EXISTS, True),  # requirement on type
        'req1': ([1, np.inf], const.REQ_CARDINALITY_FORALL, False),  # requirement on cardinality
        'req2': ({'WEU', 'EEU'}, const.REQ_CARDINALITY_EXISTS, True),  # requirement on location
        'policy': [0.4, 0.7],
        'change': []
    }
]


"""
Define services' changes using this format:
(
    'service name',
    [
        ('sd0', <sd0 new value>), 
        ...
        ('sdn', <sdn new value>)
    ]
)
"""
changes = [
    (
        's_chile',
        [
            ('sd2', 'EEU')
        ]
    ),
    (
        's_romania',
        [
            ('sd1', 15)
        ]
    ),
    (
        's_poland',
        [
            ('sd0', 'urban')
        ]
    )
]

results = walkthrough_base.execute_walkthrough(services=services, changes=changes)

if args.output_file:
    sys.stdout = open(args.output_file, 'w')

print(json.dumps(results, indent=4))
