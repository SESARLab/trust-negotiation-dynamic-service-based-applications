import copy
import dataclasses
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from dataset_generator import DatasetGenerator
from serializers import export_services_snapshot, export_negotiation_snapshot, export_dynamic_trust_snapshot
from settings_data import N_EXECUTIONS, N_TRUST_ATTRIBUTES, N_SERVICES, get_settings, N_CHANGES
from settings_model import ExperimentSetting
from simulation_model import Metadata
from simulation_sota import apply_sota
from trust_dynamic import dynamic_trust, get_action_changes, count_unstable_services
from trust_negotiation import negotiation


@dataclass
class ExperimentSingleSettingSingleRunExecutionResult:
    # metadata that are needed later to re-build the results.
    setting_name: str
    n_services: int
    n_trust_attributes: int
    execution_id: int

    negotiation_success_rate: float
    trust_value: float

    relevant_change_rate: float

    global_application_stability: float
    global_service_stability: float
    global_action_stability: float

    avg_application_stability: float
    std_application_stability: float

    avg_service_stability: float
    std_service_stability: float

    avg_action_stability: float
    std_action_stability: float

    # sota-related stuff.
    # sota-related stuff.

    sota1_success_rate: float
    sota1_trust_value: float
    sota1_unsupported_service_rate: float
    sota1_requirement_violation_rate: float

    sota2_success_rate: float
    sota2_trust_value: float
    sota2_unsupported_service_rate: float
    sota2_requirement_violation_rate: float

    sota3_success_rate: float
    sota3_trust_value: float
    sota3_unsupported_service_rate: float
    sota3_requirement_violation_rate: float


def run_single_setting_single_run(
        setting: ExperimentSetting,
        n_services: int,
        n_trust_attributes: int,
        execution_id: int,
        snapshot_dir: Path | None = None,
) -> ExperimentSingleSettingSingleRunExecutionResult:
    """
    Run one run on one setting.
    """
    # ============================================
    # 0. dataset generation.
    generator = DatasetGenerator(setting)
    dataset = generator.generate(n_services=n_services,
                                 n_trust_attributes=n_trust_attributes)

    # and prepare the stuff for export.
    metadata = Metadata(n_services=n_services,
                        n_trust_attributes=n_trust_attributes,
                        setting_name=setting.name,
                        execution_id=execution_id, )
    if snapshot_dir is not None:
        snapshot_dir.mkdir(parents=True, exist_ok=True)

    # ============================================
    # 1. initial negotiation.
    # 1.1 our approach
    negotiation_result = negotiation(dataset.services)
    initial_system = negotiation_result.included
    initial_system_snapshot = copy.deepcopy(initial_system)

    current_system = initial_system

    # 1.2 sota.
    sota_result = apply_sota(services=dataset.services)

    # 1.3 export result if required.
    if snapshot_dir is not None:
        export_services_snapshot(
            dataset=dataset,
            metadata=metadata,
            output_dir=snapshot_dir
        )

        export_negotiation_snapshot(
            negotiation_result=negotiation_result,
            sota_negotiation_result=sota_result,
            metadata=metadata,
            output_dir=snapshot_dir
        )
    # ============================================
    # define statistics
    total_changes = 0
    relevant_changes = 0

    event_application_stability = []
    event_service_stability = []
    event_action_stability = []

    # used for exports.
    dynamic_trust_events = []

    # ============================================
    # 2. begin the dynamic trust stuff.
    for tick in range(N_CHANGES):

        # no service left (very bad case, but could happen).
        if not current_system:
            break
        # assert current_system is not None and len(current_system) > 0

        # 2.1 decide if a change occurs.
        if not generator.change_occurs():
            continue

        # 2.2 select the service that changes at this moment.
        changed_service_index = generator.choose_changed_service(current_system)

        # 2.3 generate the change set for the changing service.
        change_set = generator.generate_change_set(current_system[changed_service_index])
        # # ignore empty events.
        # if not change_set.changes:
        #     continue
        # 2.3.1 increment the counter of total changes.
        total_changes += 1

        # 2.4 execute dynamic trust.
        result = dynamic_trust(
            system=current_system,
            changed_service_index=changed_service_index,
            change_set=change_set,
            debug=True  # to add more information.
        )
        # 2.4.1 debug data for exporting.
        dynamic_trust_event = {
            'tick': tick,
            'changed_service': current_system[changed_service_index].name,
            'changes': [
                {
                    'attribute_index': change.index,
                    'new_value': change.new_value
                } for change in change_set.changes
            ],
            'relevant': result.relevant,
            'application_stability': result.application_stability,
            'service_stability': result.service_stability,
            'action_stability': result.action_stability,
            'planning': {},
        }

        # 2.4.2 increment the counter of relevant events.
        if result.relevant:
            relevant_changes += 1
        # 2.4.3 update metrics.
        event_application_stability.append(result.application_stability)
        event_service_stability.append(result.service_stability)
        event_action_stability.append(result.action_stability)

        # 2.4.4 update system if
        # planning/execution happened (i.e., relevant = True).
        if result.debug_planning is not None:
            current_system = result.debug_planning.simulation.included

            # 2.4.5 update also debug data.
            dynamic_trust_event['planning'] = {
                'decision': result.debug_planning.decision,
                'included_after_planning': [
                    service.name
                    for service in
                    result.debug_planning.simulation.included
                ],
                'excluded_after_planning': [
                    service.name
                    for service in
                    result.debug_planning.simulation.excluded
                ]
            }
            if result.debug_planning.s_keep:
                dynamic_trust_event['scenario_keep'] = {
                    'services_to_remove': result.debug_planning.s_keep.services_to_remove,
                    'services_to_update': result.debug_planning.s_keep.services_to_update
                }

            if result.debug_planning.s_eviction:
                dynamic_trust_event['scenario_eviction'] = {
                    'services_to_remove': result.debug_planning.s_eviction.services_to_remove,
                    'services_to_update': result.debug_planning.s_eviction.services_to_update
                }

        if snapshot_dir is not None:
            dynamic_trust_events.append(dynamic_trust_event)

    # ============================================
    # 3. the loop is over, we begin to compute some metrics.
    final_system = current_system

    if snapshot_dir is not None:
        export_dynamic_trust_snapshot(events=dynamic_trust_events,
                                      metadata=metadata,
                                      output_dir=snapshot_dir)

    return ExperimentSingleSettingSingleRunExecutionResult(
        # 3.0 easy metrics.
        trust_value=float(np.mean([s.trust_value for s in initial_system])),
        # 3.1 metrics retrieved by comparing initial system vs final
        # negotiation success rate
        negotiation_success_rate=len(initial_system) / len(dataset.services),
        # relevant changes (out of the total changes)
        relevant_change_rate=(
            relevant_changes / total_changes
            if total_changes > 0
            else 0
        ),
        # global application stability
        global_application_stability=len(final_system) / len(initial_system_snapshot) if initial_system_snapshot else 0,
        # service stability v1: not counting expulsions.
        global_service_stability=(
            1
            - (
                    len(
                        get_action_changes(
                            original=initial_system_snapshot,
                            updated=final_system
                        )
                    )
                    / len(initial_system_snapshot)
            )
            if initial_system_snapshot else 0
        ),
        # action stability: an overall measure of stability
        global_action_stability=(
            1
            - (
                    count_unstable_services(
                        original=initial_system_snapshot,
                        updated=final_system
                    )
                    / len(initial_system_snapshot)
            )
            if initial_system_snapshot else 0
        ),
        avg_application_stability=float(np.mean(event_application_stability))
        if event_application_stability else 1.0,
        std_application_stability=float(np.std(event_application_stability))
        if event_application_stability else 0.0,
        avg_service_stability=float(np.mean(event_service_stability))
        if event_service_stability else 1.0,
        std_service_stability=float(np.std(event_service_stability))
        if event_service_stability else 0.0,
        avg_action_stability=float(np.mean(event_action_stability))
        if event_action_stability else 1.0,
        std_action_stability=float(np.std(event_action_stability))
        if event_action_stability else 0.0,
        # copy the metadata as well
        setting_name=setting.name,
        n_services=n_services,
        n_trust_attributes=n_trust_attributes,
        execution_id=execution_id,
        # sota-stuff
        # sota1
        sota1_trust_value=sota_result.sota1.trust_value,
        sota1_success_rate=sota_result.sota1.success_rate,
        sota1_unsupported_service_rate=sota_result.sota1.unsupported_service_rate,
        sota1_requirement_violation_rate=sota_result.sota1.requirement_violation_rate,
        # sota2
        sota2_trust_value=sota_result.sota2.trust_value,
        sota2_success_rate=sota_result.sota2.success_rate,
        sota2_unsupported_service_rate=sota_result.sota2.unsupported_service_rate,
        sota2_requirement_violation_rate=sota_result.sota2.requirement_violation_rate,
        # sota3
        sota3_trust_value=sota_result.sota3.trust_value,
        sota3_success_rate=sota_result.sota3.success_rate,
        sota3_unsupported_service_rate=sota_result.sota3.unsupported_service_rate,
        sota3_requirement_violation_rate=sota_result.sota3.requirement_violation_rate,
    )


import joblib
import polars as pl


def run_all_experiments(output_dir: Path | None = None, n_jobs: int = -1):
    """
    Execute all experiments.

    Returns:
        (
            raw_results,
            aggregated_results
        )

    raw_results:
        one row per execution

    aggregated_results:
        one row per
        (setting, services_num, attributes_num)
    """
    # 1. create the set of jobs that we will parallelize.
    jobs = [
        (
            setting,
            n_services,
            n_trust_attributes,
            execution_id
        )
        for setting in get_settings()
        for n_services in N_SERVICES
        for n_trust_attributes in N_TRUST_ATTRIBUTES
        for execution_id in range(N_EXECUTIONS)
    ]
    # 2. actually execute them.
    execution_results = joblib.Parallel(n_jobs=n_jobs, verbose=1)(
        joblib.delayed(run_single_setting_single_run)(
            setting=setting,
            n_services=services_num,
            n_trust_attributes=attributes_num,
            execution_id=execution_id,
            snapshot_dir=output_dir / 'snapshots' / setting.name
                       / f'services_{services_num}_attributes_{attributes_num}'
                       / f'run_{execution_id}' if output_dir else None,
        )
        for setting, services_num, attributes_num, execution_id in jobs
    )

    # 3. now we begin doing the serious stuff, that is, iterating over the results.
    # here we have *one row for each pair of setting, execution*. So pretty big.
    raw_df = pl.DataFrame([dataclasses.asdict(r) for r in execution_results])
    # what we're going to do:
    # - export the result as is
    # - export the result as the raw: group by setting (being careful over what we average/std over)
    # - export one row per setting

    # the columns for the initial grouping by
    agg1_group_cols = ['setting_name', 'n_services', 'n_trust_attributes']
    # the metrics we're going to compute avg/std over.
    agg1_metric_cols = [
        c
        for c in raw_df.columns
        if c not in {'setting_name', 'n_services', 'n_trust_attributes', 'execution_id'}
    ]
    # 3.1: export the result to average over executions for each (setting, n_serv, n_trust_attr)
    # --> basically averaging over executions
    agg1_df = (
        raw_df
        .group_by(agg1_group_cols)
        .agg(
            *[
                pl.col(c)
                .mean()
                .alias(f'avg_{c}')
                for c in agg1_metric_cols
            ],
            *[
                pl.col(c)
                .std()
                .alias(f'std_{c}')
                for c in agg1_metric_cols
            ]
        )
        .sort(agg1_group_cols)
    )
    # 3.2 export the result to average over executions for each (setting, n_serv, n_trust_attr, n_execution)
    # --> basically averaging over settings.
    agg2_group_cols = ['setting_name']
    agg2_metric_cols = [
        c
        for c in agg1_df.columns
        if c not in {'setting_name', 'n_services', 'n_trust_attributes'}
    ]
    agg2_df = (
        agg1_df
        .group_by(agg2_group_cols)
        .agg(
            *[
                pl.col(c)
                .mean()
                .alias(f'avg_{c}')
                for c in agg2_metric_cols
            ],
            *[
                pl.col(c)
                .std()
                .alias(f'std_{c}')
                for c in agg2_metric_cols
            ]
        )
        .sort('setting_name')
    )

    if output_dir:
        agg2_df.write_csv(output_dir / '01_agg2_results.csv')
        agg1_df.write_csv(output_dir / '02_agg1_results.csv')
        raw_df.write_csv(output_dir / '03_raw_results.csv')
