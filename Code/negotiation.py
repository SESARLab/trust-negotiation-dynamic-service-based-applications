#!/bin/python3

import const
from dataset_reader import getSdsFromService, getReqsFromService

def match(sd: tuple[int, bool], requirement: list[int | float] | set, certRequirement: bool) -> bool:
    """
        Function that return if a service data match a service data request
        According to how the dataset is generated:
         - service data are represented by an int/float in the range [0, 1, 2]
         - service data request are represented by a list of the form [min, max] where min is in the range [0, 1, 2]
            and max == 2. It can also be a set of acceptable values.
    """

    if certRequirement and not sd[1]:
        return False

    # if requirement is a set of acceptable values
    if isinstance(requirement, set):
        return sd[0] in requirement 

    # otherwise, it is a list.
    assert len(requirement) == 2
    return requirement[0] <= sd[0] <= requirement[1]


def matching(sds: list[tuple[int, bool]], requirement: list[tuple[list[int | float], int, bool]]) -> float:
    """
        Function that returns how much a service that made a request is satisfied from a system services' service data
        According to how the dataset is generated, every service requires every service data, and every service has every service data, so: 
         - sds is a list that contains n lists, containing all service data of each service 
         - sds[j] is a list that contains all the service data of a service
         - requirement represent the service data value requested from the requestor service in the form (range, cardinality) 
         - sds[j][i] is a service data of the same type of requirement[i]
         - we do not need to check the name of the service data

        requirement are all the requirements of a service on all service data 
    """

    satisfaction = 0
    weight = 1 / len(requirement)  # [([range], card), ...]
    # [[sd1, sd2], [t1, sd2], ...]

    for i in range(len(requirement)):  # for all the requirements # O(m) m = num sd
        count = 0

        for j in range(len(sds)):  # for each list of service data    # O(n) = n = num services
            if match(sds[j][i], requirement[i][0],
                     requirement[i][2]):  # if the service's service data match the requirement
                count += 1  # every time a service match the requirement increase the counter
                # in this way, if no services match the requirement -> count == 0
                #              if all services march the requirement -> count == len(sds)

        if (requirement[i][1] == const.REQ_CARDINALITY['FORALL'] and count == len(sds)) or (
                requirement[i][1] == const.REQ_CARDINALITY['EXISTS'] and count > 0):
            satisfaction += weight

    return satisfaction


def negotiation(services: list[dict], SoA=False, returnAll=False, excluded=None) -> list[list[dict, float]]:

    system = []
    sats = []
    excluded = [] if not excluded else excluded

    for requestor in services:
        tmp_services = services.copy()
        tmp_services.remove(requestor)

        sds = []

        for tmp_n in tmp_services:
            sds.append(getSdsFromService(tmp_n))

        sat = matching(sds, getReqsFromService(requestor))
        sats.append(sat)

        if returnAll and ((SoA and sat < 1) or (not SoA and sat < requestor['policy'][0])):
            excluded.append([requestor, sat, False])

        if (SoA and sat == 1) or (not SoA and sat > requestor['policy'][0]):
            system.append(requestor)

    if len(system) == len(services):
        if returnAll:
            for i, s in enumerate(system): 
                system[i] = [s, sats[i], True]

            for s in excluded:
                system.append(s)

            return system
        else:
            return [[n, sats[i]] for i, n in enumerate(system)]

    if returnAll:
        return negotiation(system, SoA=SoA, returnAll=True, excluded=excluded)
    else:
        return negotiation(system, SoA=SoA)


def planning(service: list[dict, float], services: list[list[dict, float]]) -> bool:
    """
        Find out if it is better to evict a changed service or keep it into the system 
    """

    #print(f"cambio {service[0]['name']}")

    evict = False

    # counters to evict
    evict_counter_action = 0
    evict_counter_service = 1

    # counters to keep 
    keep_counter_action = 0
    keep_counter_service = 0

    # tmp_services contains all services except the one who change
    tmp_services = services.copy()
    tmp_services.remove(service)

    """
        loop is on all the services except for the one who change
        This because each service needs to re-calculate its satisfaction, but not the one who change
    """

    for tmp_n in tmp_services:  # for all services except the one who changed
        """
            to check differences between evict and not evict the service: 
             1. take the system with the changed service
             2. remove the service that re-calculate satisfaction 
             3. initialize 2 lists: 
                - one containing all the other services service data including the service who changed
                - one containing the other services service data except the service who changed
             4. in a for loop add the service data in the lists. Don't add in the list to simulate the eviction if the service is the one who changed
                - evict_sds will contain service data of all services except for: the one who changed, and the one who is calculating its satisfaction  
                - evict_sds will contain service data of all services except for: the one who is calculating its satisfaction  
             5. retrieve the new satisfaction in both cases
             6. check how many services left and action changes in both cases
             7. check if it is better to evict the service or keep it 
        """

        keep_tmp_services = services.copy()  # simuate to keep -> copy the list contining the changing service
        keep_tmp_services.remove(tmp_n)

        evict_sds = []  # contains service data
        keep_sds = []

        for tmp_n2 in keep_tmp_services:
            keep_sds.append(getSdsFromService(tmp_n2[0]))

            if tmp_n2 != service:
                evict_sds.append(getSdsFromService(tmp_n2[0]))

        evict_new_sd = matching(evict_sds, getReqsFromService(tmp_n[0]))
        keep_new_sd = matching(keep_sds, getReqsFromService(tmp_n[0]))

        if (evict_new_sd < tmp_n[1]) and (
                (tmp_n[1] >= tmp_n[0]['policy'][1] and evict_new_sd < tmp_n[0]['policy'][1]) or (
                tmp_n[1] >= tmp_n[0]['policy'][0] and evict_new_sd < tmp_n[0]['policy'][0])):
            if evict_new_sd < tmp_n[0]['policy'][0]:
                evict_counter_service += 1  # if a service leave, count it
            elif evict_new_sd > tmp_n[0]['policy'][0]:
                evict_counter_action += 1  # if a service change action but not leave, count it

        if (keep_new_sd < tmp_n[1]) and (
                (tmp_n[1] >= tmp_n[0]['policy'][1] and keep_new_sd < tmp_n[0]['policy'][1]) or (
                tmp_n[1] >= tmp_n[0]['policy'][0] and keep_new_sd < tmp_n[0]['policy'][0])):
            if keep_new_sd < tmp_n[0]['policy'][0]:
                keep_counter_service += 1  # if a service leave, count it
            elif keep_new_sd > tmp_n[0]['policy'][0]:
                keep_counter_action += 1  # if a service change action but not leave, count it

    if evict_counter_service < keep_counter_service or (
            evict_counter_service == keep_counter_service and evict_counter_action < keep_counter_action):  # if eviction causes less services leaving or simulate blind planning or if eviction causes less actions changing, evict
        evict = True

    return evict


def execution(evict: bool, service: dict, services: list[list[dict, float]]):
    """
        Evict or keep a service and recalculate sds of all other services
    """

    if evict and (service in services):  # is better to evict the service
        services.remove(service)  # evict the service

    # recalculate satisfactions
    for n in services:  # for all services, with the one who changed
        tmp_services = services.copy()
        tmp_services.remove(n)
        sds = []

        for tmp_n in tmp_services:
            sds.append(getSdsFromService(tmp_n[0]))

        sat = matching(sds, getReqsFromService(n[0]))

        if sat < n[0]['policy'][0]:
            services.remove(n)
        else:
            n[1] = sat

    return services


def analysis(service: list[dict, float], services: list[list[dict, float]]) -> (bool, int):
    """
        Find out if the change of a service is relevant or not
    """

    isRelevant = False
    count = 0

    for c in service[0]['change']:  # perform changes
        newt = (c[1], service[0][c[0]][1])
        service[0][c[0]] = newt

    service[0]['change'] = []

    tmp_services = services.copy()
    tmp_services2 = tmp_services.copy()
    tmp_services.remove(service)

    if tmp_services is None:
        return isRelevant

    for tmp_n in tmp_services:  # for all services except the one who changed
        sds = []

        tmp_services2.remove(tmp_n)

        for tmp_n2 in tmp_services2:  # for all services except the one that recalculate sd
            sds.append(getSdsFromService(tmp_n2[0]))

        req = getReqsFromService(tmp_n[0])

        new_sd = matching(sds, req)

        if (new_sd < tmp_n[1]) and (tmp_n[1] >= tmp_n[0]['policy'][1] and new_sd < tmp_n[0]['policy'][1]) or (
                tmp_n[1] >= tmp_n[0]['policy'][0] and new_sd < tmp_n[0]['policy'][0]):
            isRelevant = True

            if new_sd > tmp_n[0]['policy'][0]:
                count += 1

    return isRelevant, count


def dynamicTrust(services: list[list[dict, float]]) -> (int, list[list[dict, float]], float):
    relevant_count = 0
    changes = 0
    tot_services = 0
    tmp_services = services.copy()

    for n in tmp_services:  # check every service to manage each change
        present = False

        for s in services:
            if s[0]['name'] == n[0]['name']:
                present = True
                break

        if present and ('change' in n[0] and len(n[0]['change']) > 0):
            relevant = analysis(n, tmp_services)

            if relevant[0]:
                relevant_count += 1
                changes += relevant[1]
                tot_services += len(services)

                evict = planning(n, tmp_services)

                services = execution(evict, n, tmp_services)

    return relevant_count, services, 1 - ((changes / tot_services) if tot_services > 0 else 0)
