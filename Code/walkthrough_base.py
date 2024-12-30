import dataclasses

import negotiation as neg_base
import negotiation_debug as neg_debug


def execute_walkthrough(services, changes):
    results = {}

    system = neg_base.negotiation(services, returnAll=True)

    results['in system'] = []
    results['not in system'] = []

    for e in system:
        if e[2]:
            results['in system'].append({'name': e[0]['name'], 'satisfaction': e[1]})
        else:
            results['not in system'].append({'name': e[0]['name'], 'satisfaction': e[1]})

    results['number of services in system'] = len(results['in system'])
    results['number of services not in system'] = len(results['not in system'])

    # holds a copy of the system used for dynamic trust.
    tmp_system = []
    results['changes'] = []

    # make a copy of the system in tmp_system.
    for service in system:
        if service[2]:
            tmp_system.append([service[0], service[1]])

    # for each change...
    for i, change in enumerate(changes):
        # a list of tuples
        # each element of the tuple contains (new value, old value)
        oldVal = []

        for service in tmp_system:
            # grab the service that is changing according to the name
            if service[0]['name'] == change[0]:
                for c in change[1]:
                    oldVal.append((c[0], service[0][c[0]]))

                service[0]['change'] = change[1]

        # apply dynamic trust.
        afterChange = neg_debug.dynamicTrust(tmp_system)

        changeRes = {'index': i}

        changeRes['change'] = {
            'changed service': change[0],
            'changed service data': [],
            'reason_analysis': dataclasses.asdict(afterChange[3]),
            'reason_planning': dataclasses.asdict(afterChange[4])
        }

        for c in change[1]:
            changeRes['change']['changed service data'].append({c[0]: c[1]})

        changeRes['change']['in system after change'] = []

        for service in afterChange[1]:
            changeRes['change']['in system after change'].append(
                {'name': service[0]['name'], 'satisfaction': service[1]})

        results['changes'].append(changeRes)

        tmp_system = afterChange[1]

    return results
