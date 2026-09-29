from dataclasses import dataclass

from model import ServiceWithNegotiationData, SotaServiceWithNegotiationData
from trust_core import NegotiationResult


@dataclass
class SotaNegotiationMetrics:
    """
    Detailed data returned when applying SOTA1, 2, or 3.
    """
    trust_value: float
    success_rate: float
    unsupported_service_rate: float
    requirement_violation_rate: float


@dataclass
class SotaNegotiationResult:
    sota1: SotaNegotiationMetrics
    sota2: SotaNegotiationMetrics
    sota3: SotaNegotiationMetrics

    # for export, we keep these as well.
    sota1_simulation: NegotiationResult[ServiceWithNegotiationData]
    sota2_simulation: NegotiationResult[SotaServiceWithNegotiationData]
    sota3_simulation: NegotiationResult[SotaServiceWithNegotiationData]


@dataclass
class Metadata:
    """
    Attributes:
        setting_name: name of the setting
        n_services: number of services
        n_trust_attributes: number of trusted attributes
        execution_id: int
    """
    setting_name: str
    n_services: int
    n_trust_attributes: int
    execution_id: int
