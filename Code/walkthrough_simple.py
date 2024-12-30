import json

import const
import walkthrough_base

services = [
    {
        'service': 0,
        'name': 's_chile',
        'sd0': ('national', False),  # sample type
        'sd1': ('LATAM', False),  # location
        'req0': ({'national', 'three_biggest_cities', 'urban'},
                 const.REQ_CARDINALITY_FORALL, True),  # requirement on type
        'req1': ({'EEU', 'WEU', 'LATAM'}, const.REQ_CARDINALITY_FORALL, False),  # requirement on location
        'policy': [0.4, 0.7],
        'change': []
    },
    {
        'service': 1,
        'name': 's_france',
        'sd0': ('national', True),  # sample type
        'sd1': ('WEU', True),  # location
        'req0': ({'national'}, const.REQ_CARDINALITY_EXISTS, True),  # requirement on type
        'req2': ({'WEU', 'EEU'}, const.REQ_CARDINALITY_FORALL, True),  # requirement on location
        'policy': [0.4, 0.7],
        'change': []
    },
    {
        'service': 2,
        'name': 's_poland',
        'sd0': ('national', True),  # sample type
        'sd1': ('EEU', True),  # location
        'req0': ({'national', 'three_biggest_cities', 'urban'},
                 const.REQ_CARDINALITY_FORALL, True),  # requirement on type
        'req2': ({'WEU', 'EEU', 'LATAM'}, const.REQ_CARDINALITY_FORALL, False),  # requirement on location
        'policy': [0.2, 0.5],
        'change': []
    }
]

changes = [
    (
        's_poland',
        [
            ('sd0', 'urban')
        ]
    ),
]

results = walkthrough_base.execute_walkthrough(services=services, changes=changes)

# if args.output_file:
#     sys.stdout = open(args.output_file, 'w')

print(json.dumps(results, indent=4))