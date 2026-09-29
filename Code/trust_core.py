import copy
import dataclasses
from dataclasses import dataclass
from typing import TypeVar, Generic

import settings_model
from model import Service, ServiceWithNegotiationData, TrustAttribute, TrustRequirement
from const import ACTION_EXIT

DECISION_KEEP = 'KEEP'
DECISION_REMOVE = 'EVICT'


T = TypeVar('T')


@dataclass
class NegotiationResult(Generic[T]):
    """
    Represent the result of one round of simulation.

    Attributes:
        included: list[NegotiationData] services that remain
        excluded: list[NegotiationData] services that leave
    """
    included: list[T]
    excluded: list[T]

    @classmethod
    def default(cls) -> "NegotiationResult":
        return NegotiationResult(
            included=[],
            excluded=[]
        )


def simulate_system(
        services: list[Service],
) -> NegotiationResult[ServiceWithNegotiationData]:
    """
    Perform the trust negotiation process.

    Returns:
        - included: services that remain in the final system
        - excluded: services removed during the convergence process
    """
    # services currently under evaluation
    surviving_services = copy.deepcopy(services)
    # services removed during convergence
    excluded = []
    included_next_round = [] # declared here just to please the type checker

    converged = False

    while not converged:

        included_next_round = []
        excluded_this_round = []

        for i, requestor in enumerate(surviving_services):

            other_services = surviving_services[:i] + surviving_services[i + 1:]

            # trust_value = trust_function(requestor, other_services)
            trust_value = matching(requirements=requestor.requirements, services=other_services)

            negotiation_data = ServiceWithNegotiationData.from_service(
                s=requestor,
                trust_value=trust_value)


            if negotiation_data.action != ACTION_EXIT:
                included_next_round.append(negotiation_data)
            else:
                excluded_this_round.append(negotiation_data)
        # convergence! it's that easy.

        converged = len(included_next_round)== len(surviving_services)
        # enlarge the excluded list.
        excluded.extend( excluded_this_round)
        # and update the surviving services for the next iteration.
        surviving_services =  included_next_round

    return NegotiationResult(
        included=included_next_round,
        excluded=excluded
    )


@dataclass
class ServiceWithTrustValueBasic:
    """
    Minimal wrapper for service info.

    Attributes:
        name: str the name of the service
        trust_value: float  the trust value
        action : int       the chosen action. Note that it may not match policy (e.g.,
        rejecting an improvement after dynamic trust).
    """
    name: str
    trust_value: float
    action: int

    @classmethod
    def from_service(cls, service: ServiceWithNegotiationData) -> "ServiceWithTrustValueBasic":
        return ServiceWithTrustValueBasic(
            name=service.name,
            trust_value=service.trust_value,
            action=service.action
        )


@dataclass
class PlanningScenario:
    services_to_remove: list[ServiceWithTrustValueBasic]
    services_to_update: list[ServiceWithTrustValueBasic]



@dataclass
class PlanningResult:
    """
    Represent the detailed results of phase planning.

    Note that `simulation` and `decision` are never `None`,
    while `s_eviction` and `s_keep` can be `None` (depending on whether the algorithm
    was executed setting `debug=True` (not `None`) or `debug=False` (`None`).
    """
    # the "output" of the decision taken by planning
    simulation: NegotiationResult[ServiceWithNegotiationData]
    # optional.
    s_eviction: PlanningScenario | None = dataclasses.field(default=None)
    # optional.
    s_keep: PlanningScenario    | None = dataclasses.field(default=None)
    # corresponding decision
    decision: str = dataclasses.field(default=DECISION_KEEP)


@dataclass
class DynamicTrustResult:
    """
    Result of one round of dynamic trust negotiation, containing all the relevant info.

    Attributes:
        relevant: bool indicates if the change was relevant
        application_stability: float indicates the stability of the application after dynamic trust
        service_stability: float indicates the stability of the service after dynamic trust
        action_stability: float indicates the stability of the action after dynamic trust
            (counting *any* changed action)
        debug_planning: PlanningResult | None   It is `None` when the change was not relevant.
    """
    # whether the change was relevant
    relevant: bool
    # value of application stability after this round.
    application_stability: float
    # value of service stability after this round.
    service_stability: float
    # change wrt *any* action (including exit)
    action_stability: float
    # None when the change was not relevant
    debug_planning: PlanningResult | None


def match(attribute: TrustAttribute, requirement: TrustRequirement) -> bool:
    """
    Determine whether a trust attribute matches the requirement.
    Note: this does *not* check the cardinality.
    """

    if requirement.is_certified and not attribute.is_certified:
        return False

    # if the requirement is a set, check if within the range
    if isinstance(requirement.range, set):
        return attribute.value in requirement.range

    # if not, it's a range so we see whether it fits the max/min.
    assert len(requirement.range) == 2
    # being a range, we test strict inclusion.
    # if we're on string, we don't support range checks.
    assert not isinstance(requirement.range[0], str) and not isinstance(requirement.range[1], str) and not isinstance(requirement.range[0], str) and not isinstance(attribute.value, str)
    return requirement.range[0] <= attribute.value <= requirement.range[1]


def matching(requirements: list[TrustRequirement], services: list[Service]) -> float:
    """
    Compute the trust value according to the `requirements` of a service
    against the `services`.
    """
    trust_value = 0
    weight = 1/len(requirements)

    for i in range(len(requirements)):
        # the counter starts again for each requirement, because
        # we have to decide whether the cardinality is ok.
        count = 0

        for j in range(len(services)):
            if match(services[j].attributes[i], requirements[i]):
                # increase the counter upon any positive match
                count += 1

        if (requirements[i].cardinality == settings_model.Cardinality.FORALL and count == len(services)) or (
                requirements[i].cardinality == settings_model.Cardinality.EXISTS and count > 0):
            trust_value += weight

    return trust_value
