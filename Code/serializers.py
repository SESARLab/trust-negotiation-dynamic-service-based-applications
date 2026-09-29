import dataclasses
from collections.abc import Callable
import json
from pathlib import Path
from typing import TypeVar

from dataset_generator import ExperimentalDataset
from model import ServiceWithNegotiationData, SotaServiceWithNegotiationData, TrustAttribute, TrustRequirement, Service, \
    Policy
from settings_model import Cardinality
from simulation_model import SotaNegotiationResult, SotaNegotiationMetrics, Metadata
from trust_core import NegotiationResult


def serialize_negotiation_data_our(service: ServiceWithNegotiationData) -> dict:
    return {
        'name': service.name,
        'trust_value': service.trust_value,
        'action': service.action,
    }


def serialize_negotiation_data_sota(service: SotaServiceWithNegotiationData) -> dict:
    return {
        'name': service.name,
        'trust_vector': service.trust_vector,
        'compatibility_vector': service.compatibility_vector,
        'action': service.action,
    }


T = TypeVar('T')


def serialize_negotiation_result(
        result: NegotiationResult[T],
        serializer: Callable[[T], dict]
) -> dict:
    return {
        'included': [serializer(service) for service in result.included],
        'excluded': [serializer(service) for service in result.excluded]
    }


def serialize_sota_metrics(metrics: SotaNegotiationMetrics) -> dict:
    return {
        'trust_value': metrics.trust_value,
        'success_rate': metrics.success_rate,
        'unsupported_service_rate': metrics.unsupported_service_rate,
        'requirement_violation_rate': metrics.requirement_violation_rate,
    }


def serialize_our_metrics(success_rate: float) -> dict:
    return {
        'success_rate': success_rate
    }


def export_negotiation_snapshot(
        negotiation_result: NegotiationResult[ServiceWithNegotiationData],
        sota_negotiation_result: SotaNegotiationResult,
        metadata: Metadata,
        output_dir: Path):
    """
    Export the result of a negotiation to `output_dir`.

    Parameters
        negotiation_result : NegotiationResult[ServiceWithNegotiationData]  negotiation according to our approach
        sota_negotiation_result: SotaNegotiationResult negotiation according to SOTA
        output_dir : Path where we save the results
    """

    payload = {
        'metadata': dataclasses.asdict(metadata),

        'our': {
            'metrics': serialize_our_metrics(
                len(negotiation_result.included) /
                (len(negotiation_result.included) + len(negotiation_result.excluded))),
            **serialize_negotiation_result(
                negotiation_result,
                serializer=serialize_negotiation_data_our
            )
        },

        'sota1': {
            'metrics': serialize_sota_metrics(sota_negotiation_result.sota1),
            **serialize_negotiation_result(
                sota_negotiation_result.sota1_simulation,
                serializer=serialize_negotiation_data_our # our, because it's not pairwise.
            )
        },

        'sota2': {
            'metrics': serialize_sota_metrics(sota_negotiation_result.sota2),
            **serialize_negotiation_result(
                sota_negotiation_result.sota2_simulation,
                serializer=serialize_negotiation_data_sota
            )
        },

        'sota3': {
            'metrics': serialize_sota_metrics(sota_negotiation_result.sota3),
            **serialize_negotiation_result(
                sota_negotiation_result.sota3_simulation,
                serializer=serialize_negotiation_data_sota
            )
        },
    }

    with open(output_dir / 'negotiation.json', 'w', encoding='utf-8') as fp:
        json.dump(payload, fp, indent=2)


def export_services_snapshot(
        dataset: ExperimentalDataset,
        metadata: Metadata,
        output_dir: Path
):
    payload = {
        'metadata': dataclasses.asdict(metadata),
        'services': [
            {
                'name': service.name,
                'policy': service.policy.policy,
                'attributes': [
                    {
                        'index': i,
                        'value': attribute.value,
                        'is_certified': attribute.is_certified
                    }
                    for i, attribute in enumerate(service.attributes)
                ],
                'requirements': [
                    {
                        'index': i,
                        'range_type': (
                            'set'
                            if isinstance(requirement.range, set)
                            else 'interval'
                        ),
                        'range': sorted(requirement.range)
                        if isinstance(requirement.range, set)
                        else list(requirement.range),
                        'cardinality': requirement.cardinality.name,
                        'is_certified': requirement.is_certified
                    }
                    for i, requirement in enumerate(service.requirements)]
            } for service in dataset.services]
    }

    with open(output_dir / 'services.json', 'w', encoding='utf-8') as fp:
        json.dump(payload, fp, indent=2)


def import_services_snapshot(path: Path) -> tuple[list[Service], Metadata]:
    with open(path, 'r', encoding='utf-8') as fp:
        payload = json.load(fp)

    services = []
    for service_data in payload['services']:

        attributes = [
            TrustAttribute(
                value=attribute['value'],
                is_certified=attribute['is_certified']
            )
            for attribute in service_data['attributes']
        ]

        requirements = []

        for requirement in service_data['requirements']:
            if requirement['range_type'] == 'set':
                req_range = set(requirement['range'])
            else:
                req_range = tuple(requirement['range'])

            requirements.append(
                TrustRequirement(
                    range=req_range,
                    cardinality=Cardinality[requirement['cardinality']],
                    is_certified=requirement['is_certified']
                )
            )
        services.append(Service(
            name=service_data['name'],
            policy=Policy(policy=tuple(service_data['policy'])),
            attributes=attributes,
            requirements=requirements)
        )

    metadata = Metadata(
        setting_name=payload['metadata']['setting_name'],
        n_services=payload['metadata']['n_services'],
        n_trust_attributes=payload['metadata']['n_trust_attributes'],
        execution_id=payload['metadata']['execution_id'],
    )

    return services, metadata


def export_dynamic_trust_snapshot(
        events: list[dict],
        metadata: Metadata,
        output_dir: Path
):
    payload = {
        'metadata': dataclasses.asdict(metadata),
        'events': events,
    }

    with open(output_dir / 'dynamic_trust_snapshot.json', 'w', encoding='utf-8') as fp:
        json.dump(make_json_serializable(payload), fp, indent=2)



import numpy as np


def make_json_serializable(obj):
    """
    helper for very deep objects where we just export dataclasses as is.
    """

    if dataclasses.is_dataclass(obj):
        return make_json_serializable(
            dataclasses.asdict(obj)
        )

    if isinstance(obj, dict):
        return {
            k: make_json_serializable(v)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [
            make_json_serializable(v)
            for v in obj
        ]

    if isinstance(obj, np.integer):
        return int(obj)

    if isinstance(obj, np.floating):
        return float(obj)

    if isinstance(obj, np.bool_):
        return bool(obj)

    return obj