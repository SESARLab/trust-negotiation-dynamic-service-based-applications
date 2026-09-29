import copy
from itertools import combinations

import networkx as nx
import numpy as np

from model import ServiceWithNegotiationData, Service, Policy, TrustRequirement, SotaServiceWithNegotiationData
from settings_model import Cardinality
from trust_core import matching, NegotiationResult, simulate_system, match


def compute_pairwise_trust_value(service: Service,
                                 other_services: list[Service]) -> float:
    """
    Compute the pairwise trust value of a service

    - 1:1 matching with any other service
    - pick the minimum
    """
    pairwise_values = [
        matching(
            requirements=service.requirements,
            services=[other_service]
        )
        for other_service in other_services if other_service != service
    ]

    return float(np.min(pairwise_values)) if pairwise_values else 0


def negotiation_sota1(services: list[Service]) -> NegotiationResult[ServiceWithNegotiationData]:
    services_copy = copy.deepcopy(services)

    for service in services_copy:
        # it's that easy!
        service.policy = Policy(policy=(1.0,))

    return simulate_system(services=services_copy)


def build_trust_matrix(
        services: list[Service]
) -> tuple[dict[str, dict[str, float]], dict[str, dict[str, bool]]]:
    """
    Compute pairwise trust values.

    T[i][j] represents the trust value computed by
    matching service i requirements against service j.

    Indexes are the service names.

    We use the same matching of the main approach.

    For the binarized trust, we use the formula
    :math:`binary_matrix[i][j] = I(matrix[i][j]) >= min(policy(i))`, where
    :math:`I` is the indicator function.
    """
    matrix = {}
    binary_matrix = {}

    for requestor in services:

        threshold = min(requestor.policy.policy)

        matrix[requestor.name] = {}
        binary_matrix[requestor.name] = {}

        for other in services:

            # trust against itself is 1
            if requestor == other:
                matrix[requestor.name][other.name] = 1.0
                binary_matrix[requestor.name][other.name] = 1
                continue

            # or do the actual matching.
            matrix[requestor.name][other.name] = matching(
                requirements=requestor.requirements,
                services=[other]
            )
            binary_matrix[requestor.name][other.name] = matrix[requestor.name][other.name] >= threshold

    return matrix, binary_matrix

def build_compatibility_graph(
        services: list[Service],
        compatibility_matrix: dict[str, dict[str, bool]]
) -> nx.Graph:
    """
    Create an undirected graph containing only mutual
    compatibility relationships.
    """

    graph = nx.Graph()

    for service in services:
        graph.add_node(service.name)

    # for each pair of services
    for service_i in services:
        for service_j in services:

            # of course don't add self-loops
            if service_i == service_j:
                continue

            # we see whether they are compatible.
            if (compatibility_matrix[service_i.name][service_j.name] and
                    compatibility_matrix[service_j.name][service_i.name]):
                # and if so, draw the edge.
                graph.add_edge(service_i.name, service_j.name)

    return graph


def clique_score(
        clique: list[str],
        trust_matrix: dict[str, dict[str, float]]
) -> float:
    """
    mean the pairwise trust values of all internal edges.

    The mean considers *only* the trust of the services part of the clique,
    namely only of the services part of the application.

    Parameters:
        clique (list[str]) the services in the clique
        trust_matrix (dict[str, dict[str, float]]) the trust matrix with raw values.
    """

    values = []

    for s1, s2 in combinations(clique, 2):
        values.append(trust_matrix[s1][s2])
        values.append(trust_matrix[s2][s1])

    return float(np.mean(values)) if values else 0


def find_best_clique(
        graph: nx.Graph,
        trust_matrix: dict[str, dict[str, float]]
) -> list[str]:
    """
    Select the largest clique.

    If multiple maximum cliques exist,
    select the one maximizing internal trust.
    """

    cliques = list(nx.find_cliques(graph))

    if not cliques:
        return []

    # compute the maximum length of the clique(s)
    max_size = max(len(clique) for clique in cliques)
    # and filter out those that are smaller.
    candidate_cliques = [clique for clique in cliques if len(clique) == max_size]

    # finally, we retrieve the clique with the highest score.
    return max(candidate_cliques,
               key=lambda clique: clique_score(clique, trust_matrix)
               )


def negotiation_sota2(
        services: list[Service]
) -> NegotiationResult[SotaServiceWithNegotiationData]:

    trust_matrix, binary_trust_matrix = build_trust_matrix(services)

    graph = build_compatibility_graph(services=services, compatibility_matrix=binary_trust_matrix)

    selected_names = set(
        find_best_clique(
            graph,
            trust_matrix
        )
    )

    # a 1-service composition does not make any sense.
    # if so, "force" to an empty composition.
    if len(selected_names) < 2:
        selected_names = set()

    # build the result
    included = []
    excluded = []

    for service in services:
        if service.name in selected_names:
            included.append(SotaServiceWithNegotiationData.from_service(
                s=service,
                trust_vector=trust_matrix[service.name],
                compatibility_vector=binary_trust_matrix[service.name],
                enters=False
            ))
        else:
            excluded.append(SotaServiceWithNegotiationData.from_service(
                s=service,
                trust_vector=trust_matrix[service.name],
                compatibility_vector=binary_trust_matrix[service.name],
                enters=False
            ))

    return NegotiationResult(included=included, excluded=excluded)


def negotiation_sota3(
        services: list[Service]
) -> NegotiationResult[SotaServiceWithNegotiationData]:
    """
    Pairwise compatibility-based negotiation
    using a strict policy [1].
    """

    services_copy = copy.deepcopy(services)

    for service in services_copy:
        service.policy = Policy(policy=(1.0,))

    # it's as easy as it gets!
    return negotiation_sota2(services_copy)


def is_requirement_satisfied(
        requirement: TrustRequirement,
        attribute_index: int,
        services: list[Service]
) -> bool:
    """
    Check if `requirement` is satisfied by all `services`. The attribute to check against
    is identified by `attribute_index`.
    """

    count = 0

    for service in services:

        if match(service.attributes[attribute_index], requirement):
            count += 1

    # if forall, the counter must be equal to the length of services.
    if requirement.cardinality == Cardinality.FORALL:
        return count == len(services)
    # otherwise it is an exists, so >0 is sufficient.
    return count > 0


def evaluate_sota_composition(
        simulation: NegotiationResult[ServiceWithNegotiationData] | NegotiationResult[SotaServiceWithNegotiationData],
) -> tuple[float, float]:
    """
    Returns:
        (
            unsupported_service_rate,
            requirement_violation_rate
        )
    """

    included = simulation.included

    # rare case but could happen.
    if not included:
        return 0.0, 0.0

    # number of services that should not enter.
    unsupported = 0
    # number of req violated/total reqs for each service.
    service_requirement_violation_rate = []

    # for each service, we compute the actual trust using our approach.
    for i, service in enumerate(included):
        # number of requirements violated, i.e., really *not* supported.
        violated_requirements = 0

        # the other services.
        other_services = included[:i] + included[i + 1:]

        # trust value according to our approach.
        tv_global = matching(requirements=service.requirements, services=other_services)

        # see whether the service could actually enter.
        threshold = min(service.policy.policy)
        # if the trust value is below the threshold *according to our approach*
        # then it should have not entered
        if tv_global < threshold:
            unsupported += 1

        # now, we check the requirements.
        for req_idx, requirement in enumerate(service.requirements):

            if not is_requirement_satisfied(services=other_services,
                                            requirement=requirement,
                                            attribute_index=req_idx):
                violated_requirements += 1
        service_requirement_violation_rate.append(violated_requirements / len(service.requirements))

        # the gap is given by (max_trust_value - retrieved_trust_value)
        # total_gap += 1.0 - tv_global

    return (
        unsupported / len(included),
        float(np.mean(service_requirement_violation_rate))
        if len(service_requirement_violation_rate) > 0 else 0.0,
    )
