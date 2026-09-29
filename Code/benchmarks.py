import copy
import dataclasses
from pathlib import Path

import numpy as np
import pytest

from dataset_generator import DatasetGenerator
from model import Service, ChangeSet, ServiceWithNegotiationData, TrustAttributeChange
from serializers import import_services_snapshot
from settings_data import get_settings, TRUST_ATTRIBUTE_VALUE_BAD
from settings_model import ExperimentSetting
from simulation_model import Metadata
from trust_core import NegotiationResult
import trust_dynamic    # this way to support monkey patch.
from trust_negotiation import negotiation


# for monkey-patching. Otherwise, we end up with double recursion.
ORIGINAL_ANALYSIS = trust_dynamic.analysis


@pytest.mark.benchmark(
    group = 'negotiation',
    min_rounds = 50,
    disable_gc = True,
    warmup = True
)
def test_negotiation(benchmark, request):
    services, _ = get_services_and_build_benchmark(benchmark, request)
    benchmark(negotiation, services)


@pytest.mark.benchmark(
    group = 'dynamic_trust',
    # min_rounds = 50,
    disable_gc = True,
    warmup = True
)
def test_dynamic_trust(benchmark, request, monkeypatch):

    # get settings and generate change.
    after, changed_service_index, change_set = build_all_for_dynamic_trust(benchmark, request)

    original_system = after.included

    # apply monkey-patching.
    monkeypatch.setattr(trust_dynamic, 'analysis', wrap_analysis)

    # this is needed because dynamic_trust modifies the system,
    # and we need to ensure that each invocation of the benchmark receives the same data.
    def setup():
        system = copy.deepcopy(original_system)

        return (
            (
                system,
                changed_service_index,
                change_set
            ),
            {}
        )

    # we need to be more conservative because there's no automatic calibration.
    benchmark.pedantic(trust_dynamic.dynamic_trust, setup=setup, rounds=100, warmup_rounds=10)

    # and benchmark!
    #benchmark(dynamic_trust, after.included, changed_service_index, change_set)


@pytest.mark.benchmark(
    group = 'dynamic_trust',
    min_rounds = 50,
    disable_gc = True,
    warmup = True
)
def test_dynamic_analysis(benchmark, request):
    # get settings and generate change.
    after, changed_service_index, change_set = build_all_for_dynamic_trust(benchmark, request)

    # here we need to apply the change before executing.
    after.included[changed_service_index].apply_change(change_set)

    # and benchmark!
    benchmark(trust_dynamic.analysis, after.included, changed_service_index)


@pytest.mark.benchmark(
    group = 'dynamic_trust',
    min_rounds = 50,
    disable_gc = True,
    warmup = True
)
def test_dynamic_planning(benchmark, request):
    # get settings and generate change.
    after, changed_service_index, change_set = build_all_for_dynamic_trust(benchmark, request)

    # here we need to apply the change before executing.
    after.included[changed_service_index].apply_change(change_set)

    # and benchmark!
    benchmark(trust_dynamic.planning, after.included, changed_service_index)


# some helpers from here.
def wrap_analysis(system: list[ServiceWithNegotiationData], changed_service_index: int) -> bool:
    """
    A generate change may not be relevant no matter how hard we try. To force the analysis, we use this modified
    version of the analysis.
    """
    ORIGINAL_ANALYSIS(system, changed_service_index)
    return True


def build_all_for_dynamic_trust(
        benchmark, request
) -> tuple[NegotiationResult[ServiceWithNegotiationData], int, ChangeSet]:
    """
    Build the initial negotiated system and generate a potentially relevant change.
    The generated change is *not* applied to the system.

    Returns:
        - system after the negotiation
        - index of the changed service
        - change set

    """
    services, metadata = get_services_and_build_benchmark(benchmark, request)
    # do the negotiation.
    after = negotiation(services)
    # choose randomly a service
    # select only services for which at least one attribute can be degraded.
    degradable_service_indices = [
        i
        for i, service in enumerate(after.included)
        if any(
            attribute.value != TRUST_ATTRIBUTE_VALUE_BAD
            for attribute in service.attributes
        )
    ]
    # skip. But won't happen.
    if not degradable_service_indices:
        # pytest.skip('No service with degradable trust attributes.')
        # don't care.
        degradable_service_indices = list(range(len(services)))

    # randomly choose one of the degradable services.
    changed_service_index = int(np.random.default_rng().choice(degradable_service_indices))

    changed_service = after.included[changed_service_index]

    # generate a heavy change by degrading all applicable attributes.
    changes = [
        TrustAttributeChange(
            i,
            TRUST_ATTRIBUTE_VALUE_BAD
        )
        for i, attribute in enumerate(changed_service.attributes)
        if attribute.value != TRUST_ATTRIBUTE_VALUE_BAD
    ]

    return after, changed_service_index, ChangeSet(changes=tuple(changes))


def get_services_and_build_benchmark(benchmark, request) -> tuple[list[Service], Metadata]:
    """
    Returns the services at `request.config.getoption('--dataset-dir')`, and fills `benchmark.extra_info` with
    the corresponding metadata.
    """
    services, metadata = import_services_snapshot(Path(request.config.getoption('--dataset-dir')))
    # add extra info to the benchmark.
    for k, v in dataclasses.asdict(metadata).items():
        benchmark.extra_info[k] = v
    return services, metadata


def get_setting_from_metadata(metadata: Metadata) -> tuple[ExperimentSetting, list[ExperimentSetting]]:
    settings = get_settings()
    current_setting = None

    for setting in settings:
        if setting.name == metadata.setting_name:
            current_setting = setting
    if current_setting is None:
        raise Exception(f'setting not found: {metadata.setting_name}, got: {[s.name for s in settings]}')
    return current_setting, settings


def build_change(current_setting: ExperimentSetting, services: list[Service]) -> tuple[int, ChangeSet]:
    generator = DatasetGenerator(current_setting)
    changed_service_index = generator.choose_changed_service(services)
    change_set = generator.generate_change_set(services[changed_service_index])
    return changed_service_index, change_set
