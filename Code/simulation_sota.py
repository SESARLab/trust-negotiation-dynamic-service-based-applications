import copy

import numpy as np

from model import Service
from simulation_model import SotaNegotiationResult, SotaNegotiationMetrics
from trust_sota import negotiation_sota1, negotiation_sota2, negotiation_sota3, evaluate_sota_composition


def apply_sota(services: list[Service]) -> SotaNegotiationResult:

    # 1. negotiate
    sota1_result = negotiation_sota1(copy.deepcopy(services))
    sota2_result = negotiation_sota2(copy.deepcopy(services))
    sota3_result = negotiation_sota3(copy.deepcopy(services))

    services_num = len(services)

    # 2. evaluate the quality.
    sota1_unsupported, sota1_violations = evaluate_sota_composition(sota1_result)
    sota2_unsupported, sota2_violations = evaluate_sota_composition(sota2_result)
    sota3_unsupported, sota3_violations = evaluate_sota_composition(sota3_result)

    return SotaNegotiationResult(
        sota1=SotaNegotiationMetrics(
            trust_value=float(np.mean([s.trust_value for s in sota1_result.included])) if len(sota1_result.included) > 0 else 0.0,
            success_rate=(
                len(sota1_result.included)
                / services_num
                if services_num > 0 else 0
            ),
            unsupported_service_rate=sota1_unsupported,
            requirement_violation_rate=sota1_violations
        ),
        sota2=SotaNegotiationMetrics(
            trust_value=float(np.mean([s.trust_value for s in sota2_result.included])) if len(sota2_result.included) > 0 else 0.0,
            success_rate=(
                len(sota2_result.included)
                / services_num
                if services_num > 0 else 0
            ),
            unsupported_service_rate=sota2_unsupported,
            requirement_violation_rate=sota2_violations
        ),
        sota3=SotaNegotiationMetrics(
            trust_value=float(np.mean([s.trust_value for s in sota3_result.included])) if len(sota3_result.included) > 0 else 0.0,
            success_rate=(
                len(sota3_result.included)
                / services_num
                if services_num > 0 else 0
            ),
            unsupported_service_rate=sota3_unsupported,
            requirement_violation_rate=sota3_violations
        ),

        sota1_simulation=sota1_result,
        sota2_simulation=sota2_result,
        sota3_simulation=sota3_result
    )
