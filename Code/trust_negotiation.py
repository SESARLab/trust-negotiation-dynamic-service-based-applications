from model import Service, ServiceWithNegotiationData
from trust_core import NegotiationResult, simulate_system, matching


def negotiation(services: list[Service]) -> NegotiationResult[ServiceWithNegotiationData]:
    """
    Computes the set of services that join the application
    and their corresponding trust values.
    """

    return simulate_system(services=services)
