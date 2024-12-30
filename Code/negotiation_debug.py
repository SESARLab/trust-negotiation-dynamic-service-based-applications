import dataclasses
import typing

import negotiation


DECISION_KEEP = 'KEEP'
DECISION_REMOVE = 'EVICT'


@dataclasses.dataclass
class DebugOutputAnalysis:
    affected_services: typing.List[str] = dataclasses.field(default_factory=list)

    @staticmethod
    def default():
        return DebugOutputAnalysis()


@dataclasses.dataclass
class DebugOutputPlanning:
    decision: str = dataclasses.field(default=DECISION_KEEP)
    evict_service_to_remove: typing.List[str] = dataclasses.field(default_factory=list)
    evict_service_to_update: typing.List[str] = dataclasses.field(default_factory=list)

    keep_service_to_remove: typing.List[str] = dataclasses.field(default_factory=list)
    keep_service_to_update: typing.List[str] = dataclasses.field(default_factory=list)

    @staticmethod
    def default():
        return DebugOutputPlanning()


def dynamicTrust(services: list[list[dict, float]]
                 ) -> (int, list[list[dict, float]], float, DebugOutputAnalysis, DebugOutputPlanning):
    relevant_count = 0
    changes = 0
    tot_services = 0
    tmp_services = services.copy()

    debug_output_analysis = DebugOutputAnalysis.default()
    debug_output_planning = DebugOutputPlanning.default()

    for n in tmp_services:  # check every service to manage each change
        present = False

        for s in services:
            if s[0]['name'] == n[0]['name']:
                present = True
                break

        if present and ('change' in n[0] and len(n[0]['change']) > 0):
        # if present:
        #     worsening = False
        #
        #     if 'change' in n[0]:
        #         for c in n[0]['change']:
        #             if c[1] < n[0][c[0]][0]:
        #                 worsening = True
        #                 break
        #
        #     if ('change' in n[0] and len(n[0][
        #                                      'change']) > 0) and worsening:
                # if the service change a service data and the change is a worsening
                relevant = analysis(n, tmp_services)

                if relevant[0]:
                    relevant_count += 1
                    changes += relevant[1]
                    tot_services += len(services)

                    debug_output_analysis = relevant[2]

                    evict, debug_output_planning = planning(n, tmp_services)

                    services = negotiation.execution(evict, n, tmp_services)

    return relevant_count, services, 1 - ((changes / tot_services) if tot_services > 0 else 0), debug_output_analysis, debug_output_planning


def analysis(service: list[dict, float], services: list[list[dict, float]]) -> (bool, int, DebugOutputAnalysis):
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
    tmp_services.remove(service)

    if tmp_services is None:
        return isRelevant

    affected_services_ = []

    for tmp_n in tmp_services:  # for all services except the one who changed
        tmp_services2 = services.copy()
        sds = []

        tmp_services2.remove(tmp_n)

        for tmp_n2 in tmp_services2:  # for all services except the one that recalculate sd
            sds.append(negotiation.getSdsFromService(tmp_n2[0]))

        req = negotiation.getReqsFromService(tmp_n[0])

        new_sd = negotiation.matching(sds, req)

        # print(tmp_n)

        if (new_sd < tmp_n[1]) and (tmp_n[1] >= tmp_n[0]['policy'][1] and new_sd < tmp_n[0]['policy'][1]) or (
                tmp_n[1] >= tmp_n[0]['policy'][0] and new_sd < tmp_n[0]['policy'][0]):
            isRelevant = True

            affected_services_.append(tmp_n[0]['name'])

            if new_sd > tmp_n[0]['policy'][0]:
                count += 1

    return isRelevant, count, DebugOutputAnalysis(affected_services=affected_services_)

def planning(service: list[dict, float], services: list[list[dict, float]]) -> (bool, DebugOutputPlanning):
    """
        Find out if it is better to evict a changed service or keep it into the system
    """

    evict = False

    # counters to evict
    evict_counter_action = 0
    evict_counter_service = 1

    # counters to keep
    keep_counter_action = 0
    keep_counter_service = 0

    # for debug
    evict_service_to_remove = []
    evict_service_to_update = []
    keep_service_to_remove = []
    keep_service_to_update = []

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
            keep_sds.append(negotiation.getSdsFromService(tmp_n2[0]))

            if tmp_n2 != service:
                evict_sds.append(negotiation.getSdsFromService(tmp_n2[0]))

        evict_new_sd = negotiation.matching(evict_sds, negotiation.getReqsFromService(tmp_n[0]))
        keep_new_sd = negotiation.matching(keep_sds, negotiation.getReqsFromService(tmp_n[0]))

        if (evict_new_sd < tmp_n[1]) and (
                (tmp_n[1] >= tmp_n[0]['policy'][1] and evict_new_sd < tmp_n[0]['policy'][1]) or (
                tmp_n[1] >= tmp_n[0]['policy'][0] and evict_new_sd < tmp_n[0]['policy'][0])):
            if evict_new_sd < tmp_n[0]['policy'][0]:
                evict_counter_service += 1  # if a service leave, count it

                evict_service_to_remove.append(tmp_n[0]['name'])

            elif evict_new_sd > tmp_n[0]['policy'][0]:
                evict_counter_action += 1  # if a service change action but not leave, count it

                evict_service_to_update.append(tmp_n[0]['name'])

        if (keep_new_sd < tmp_n[1]) and (
                (tmp_n[1] >= tmp_n[0]['policy'][1] and keep_new_sd < tmp_n[0]['policy'][1]) or (
                tmp_n[1] >= tmp_n[0]['policy'][0] and keep_new_sd < tmp_n[0]['policy'][0])):
            if keep_new_sd < tmp_n[0]['policy'][0]:
                keep_counter_service += 1  # if a service leave, count it

                keep_service_to_remove.append(tmp_n[0]['name'])

            elif keep_new_sd > tmp_n[0]['policy'][0]:
                keep_counter_action += 1  # if a service change action but not leave, count it

                keep_service_to_update.append(tmp_n[0]['name'])

    if evict_counter_service < keep_counter_service or (
            evict_counter_service == keep_counter_service and evict_counter_action < keep_counter_action):  # if eviction causes less services leaving or simulate blind planning or if eviction causes less actions changing, evict
        evict = True

    return evict, DebugOutputPlanning(
        evict_service_to_remove=evict_service_to_remove, evict_service_to_update=evict_service_to_update,
        keep_service_to_remove=keep_service_to_remove, keep_service_to_update=keep_service_to_update,
        decision=DECISION_REMOVE if evict else DECISION_KEEP)