import json

import numpy as np

from model import Service, TrustAttribute, TrustRequirement, Policy, ChangeSet, TrustAttributeChange
from settings_model import Cardinality
from walkthrough_base import execute_walkthrough

services = [
    Service(
        name='s_brazil',
        attributes=[
            # sample type
            TrustAttribute(value='three_biggest_cities', is_certified=False),
            # cardinality
            TrustAttribute(value=25, is_certified=False),
            # location
            TrustAttribute(value='WEU', is_certified=False)
        ],
        requirements=[
            # sample type
            TrustRequirement(range={'national', 'three_biggest_cities', 'urban'},
                             cardinality=Cardinality.FORALL,
                             is_certified=True),
            # cardinality
            TrustRequirement(range=(20, np.inf), cardinality=Cardinality.FORALL,
                             is_certified=False),
            # location
            TrustRequirement(range={'WEU', 'LATAM'}, cardinality=Cardinality.EXISTS,
                             is_certified=False),
        ],
        policy=Policy(policy=(0.4, 0.6), )
    ),
    Service(
        name='s_chile',
        attributes=[
            # sample type
            TrustAttribute(value='national', is_certified=False),
            # cardinality
            TrustAttribute(value=25, is_certified=False),
            # location
            TrustAttribute(value='LATAM', is_certified=False)
        ],
        requirements=[
            # sample type
            TrustRequirement(range={'national', 'three_biggest_cities', 'urban'},
                             cardinality=Cardinality.FORALL,
                             is_certified=True),
            # cardinality
            TrustRequirement(range=(1, np.inf), cardinality=Cardinality.FORALL,
                             is_certified=False),
            # location
            TrustRequirement(range={'EEU', 'WEU', 'LATAM'},
                             cardinality=Cardinality.FORALL,
                             is_certified=False),
        ],
        policy=Policy(policy=(0.4, 0.7), )
    ),

    Service(
        name='s_france',
        attributes=[
            # sample type
            TrustAttribute(value='national', is_certified=True),
            # cardinality
            TrustAttribute(value=30, is_certified=True),
            # location
            TrustAttribute(value='WEU', is_certified=True)
        ],
        requirements=[
            # sample type
            TrustRequirement(range={'national'},
                             cardinality=Cardinality.EXISTS,
                             is_certified=True),
            # cardinality
            TrustRequirement(range=(1, np.inf), cardinality=Cardinality.FORALL,
                             is_certified=False),
            # location
            TrustRequirement(range={'WEU', 'EEU'},
                             cardinality=Cardinality.FORALL,
                             is_certified=True),
        ],
        policy=Policy(policy=(0.4, 0.7), )
    ),

    Service(
        name='s_italy',
        attributes=[
            # sample type
            TrustAttribute(value='national', is_certified=True),
            # cardinality
            TrustAttribute(value=30, is_certified=True),
            # location
            TrustAttribute(value='WEU', is_certified=True)
        ],
        requirements=[
            # sample type
            TrustRequirement(range={'national', 'three_biggest_cities', 'urban'},
                             cardinality=Cardinality.FORALL,
                             is_certified=True),
            # cardinality
            TrustRequirement(range=(30, np.inf), cardinality=Cardinality.FORALL,
                             is_certified=False),
            # location
            TrustRequirement(range={'EEU', 'WEU'},
                             cardinality=Cardinality.EXISTS,
                             is_certified=True),
        ],
        policy=Policy(policy=(1,), )
    ),

    Service(
        name='s_mexico',
        attributes=[
            # sample type
            TrustAttribute(value='three_biggest_cities', is_certified=False),
            # cardinality
            TrustAttribute(value=25, is_certified=False),
            # location
            TrustAttribute(value='LATAM', is_certified=False)
        ],
        requirements=[
            # sample type
            TrustRequirement(range={'national', 'three_biggest_cities', 'urban'},
                             cardinality=Cardinality.FORALL,
                             is_certified=True),
            # cardinality
            TrustRequirement(range=(25, np.inf), cardinality=Cardinality.FORALL,
                             is_certified=False),
            # location
            TrustRequirement(range={'LATAM'},
                             cardinality=Cardinality.EXISTS,
                             is_certified=False),
        ],
        policy=Policy(policy=(0.2, 0.5), )
    ),

    Service(
        name='s_poland',
        attributes=[
            # sample type
            TrustAttribute(value='national', is_certified=True),
            # cardinality
            TrustAttribute(value=28, is_certified=True),
            # location
            TrustAttribute(value='EEU', is_certified=True)
        ],
        requirements=[
            # sample type
            TrustRequirement(range={'national', 'three_biggest_cities', 'urban'},
                             cardinality=Cardinality.FORALL,
                             is_certified=True),
            # cardinality
            TrustRequirement(range=(1, np.inf), cardinality=Cardinality.FORALL,
                             is_certified=False),
            # location
            TrustRequirement(range={'WEU', 'EEU', 'LATAM'},
                             cardinality=Cardinality.FORALL,
                             is_certified=False),
        ],
        policy=Policy(policy=(0.2, 0.5), )
    ),

    Service(
        name='s_romania',
        attributes=[
            # sample type
            TrustAttribute(value='national', is_certified=True),
            # cardinality
            TrustAttribute(value=35, is_certified=True),
            # location
            TrustAttribute(value='EEU', is_certified=True)
        ],
        requirements=[
            # sample type
            TrustRequirement(range={'national'},
                             cardinality=Cardinality.EXISTS,
                             is_certified=True),
            # cardinality
            TrustRequirement(range=(1, np.inf), cardinality=Cardinality.FORALL,
                             is_certified=False),
            # location
            TrustRequirement(range={'WEU', 'EEU'},
                             cardinality=Cardinality.EXISTS,
                             is_certified=True),
        ],
        policy=Policy(policy=(0.4, 0.7), )
    )
]

changes = [
    (
        's_chile',
        ChangeSet(changes=(TrustAttributeChange(index=2, new_value='EEU'),))
    ),
    (
        's_romania',
        ChangeSet(changes=(TrustAttributeChange(index=1, new_value=15),))
    ),
    (
        's_poland',
        ChangeSet(changes=(TrustAttributeChange(index=0, new_value='urban'),))
    )
]

results = execute_walkthrough(services, changes)
print(json.dumps(results, indent=2))
