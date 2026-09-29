import copy

from const import DECISION_KEEP, DECISION_REMOVE
from model import ServiceWithNegotiationData, ChangeSet, worsened
from trust_core import NegotiationResult, simulate_system, PlanningResult, PlanningScenario, DynamicTrustResult, \
    matching, ServiceWithTrustValueBasic


def dynamic_trust(system: list[ServiceWithNegotiationData],
                  changed_service_index: int,
                  change_set: ChangeSet,
                  debug: bool = False) -> DynamicTrustResult:
    """
    Execute the dynamic trust protocol for a single change event.

    The change is assumed to affect only one service, as described
    in the paper.
    """

    #
    # Save the system before the change.
    #
    before_system = copy.deepcopy(system)

    # ============================================
    # 0. apply the change
    system[changed_service_index].apply_change(change_set)

    # ============================================
    # 1. analysis.
    relevant = analysis(system=system, changed_service_index=changed_service_index)
    # nothing happens.
    if not relevant:
        return DynamicTrustResult(
            relevant=False,
            application_stability=1,
            service_stability=1,
            action_stability=1,
            debug_planning=None
        )

    # ============================================
    # 2. planning.
    planning_result = planning(
        changed_service_index=changed_service_index,
        system=system,
        debug=debug,
    )

    # ============================================
    # 3. execution.
    after_system = execution(planning_result)

    # ============================================
    # 4. some post measures.
    # 4.1 application stability.
    application_stability = (
        len(after_system.included)
        / len(before_system)
        if len(before_system) > 0 else 0
    )
    # 4.2 service stability.
    action_changes = len(get_action_changes(original=before_system, updated=after_system.included))
    service_stability = (
        1.0 - (action_changes / len(before_system))
        if len(before_system) > 0 else 0
    )
    # 4.3 action stability
    action_stability = (1.0 -
                        count_unstable_services(before_system, after_system.included) /
                        len(before_system)
                        if len(before_system) > 0 else 0)

    return DynamicTrustResult(
        relevant=True,
        application_stability=application_stability,
        service_stability=service_stability,
        action_stability=action_stability,
        debug_planning=planning_result
    )


def analysis(system: list[ServiceWithNegotiationData], changed_service_index: int) -> bool:
    """
    Determine whether a change is relevant.

    A change is relevant if it causes at least one other service
    to worsen its action.
    """

    # ============================================

    # ============================================
    # 2. recompute trust values only for the other services.
    for i, service in enumerate(system):

        if i == changed_service_index:
            continue

        # all but this one.
        other_services = system[:i] + system[i + 1:]

        new_trust_value = matching(
            requirements=service.requirements,
            services=other_services
        )

        # if at least one service worsens, we return True and stop here.
        # no need to do a full scan.
        if new_trust_value < service.trust_value and worsened(
                old_tv=service.trust_value,
                new_tv=new_trust_value,
                policy=service.policy
        ):
            return True

    return False


def planning(system: list[ServiceWithNegotiationData], changed_service_index: int,
             debug: bool = False) -> PlanningResult:
    """
    Decide whether keeping or evicting the changed service
    maximizes application stability and, secondarily,
    service stability.
    """

    # ============================================
    # 1. simulate keep.
    system_keep = copy.deepcopy(system)
    simulation_keep = simulate_system(services=system_keep)

    # ============================================
    # 2. simulate evict.
    system_evict = copy.deepcopy(system)
    system_evict = system_evict[:changed_service_index] + system_evict[changed_service_index + 1:]
    simulation_evict = simulate_system(services=system_evict)

    # normalize, de-updating actions. This is needed because the simulation
    # may have increased the trust value and consequently the action. Here, we revert the action
    # to the previous one (only when applicable, that is, only in case of trust value improvement).
    simulation_keep = freeze_improvements(original=system, updated=simulation_keep)
    simulation_evict = freeze_improvements(original=system, updated=simulation_evict)

    # ============================================
    # 3. prepare result object
    result = PlanningResult(
        simulation=NegotiationResult.default(),
        s_eviction=PlanningScenario(
            services_to_remove=[ServiceWithTrustValueBasic.from_service(s) for s in simulation_evict.excluded],
            services_to_update=get_action_changes(original=system, updated=simulation_evict.included),
        ) if debug else None,  # add data only if needed.
        s_keep=PlanningScenario(
            services_to_remove=[ServiceWithTrustValueBasic.from_service(s) for s in simulation_keep.excluded],
            services_to_update=get_action_changes(original=system, updated=simulation_keep.included),
        ) if debug else None  # add data only if needed.
    )

    # ============================================
    # 4. application stability
    survivors_keep = len(simulation_keep.included)
    survivors_evict = len(simulation_evict.included)
    # let's see whether it is sufficient.
    if survivors_keep > survivors_evict:
        result.decision = DECISION_KEEP
        result.simulation = simulation_keep
        return result

    if survivors_evict > survivors_keep:
        result.decision = DECISION_REMOVE
        result.simulation = simulation_evict
        return result

    # ============================================
    # 5. service stability
    changes_keep = count_changed_actions(original=system, updated=simulation_keep.included)
    changes_evict = count_changed_actions(original=system, updated=simulation_evict.included)

    if changes_keep < changes_evict:
        result.decision = DECISION_KEEP
        result.simulation = simulation_keep
        return result

    if changes_evict < changes_keep:
        result.decision = DECISION_REMOVE
        result.simulation = simulation_evict
        return result

    # ============================================
    # 6. in case of further tie
    result.decision = DECISION_KEEP
    result.simulation = simulation_keep

    return result


def execution(result: PlanningResult) -> NegotiationResult:
    """
    Pretty basic but we already have the resulting system.
    """
    return result.simulation


def freeze_improvements(
        original: list[ServiceWithNegotiationData],
        updated: NegotiationResult[ServiceWithNegotiationData]
) -> NegotiationResult:
    """
    Prevent action improvements.

    Trust values are preserved, but actions cannot become
    better than those in the original system.
    """

    original_by_name = {
        s.name: s
        for s in original
    }

    for service in updated.included:

        original_service = original_by_name.get(
            service.name
        )

        if original_service is None:
            continue

        if service.action > original_service.action:
            # force the action.
            service.set_action(original_service.action, force=True)

    return updated


def get_action_changes(original: list[ServiceWithNegotiationData], updated: list[ServiceWithNegotiationData]) -> list[
    ServiceWithTrustValueBasic]:
    """
    Returns the names of services whose action changed
    and that are still present in the system.
    """

    updated_by_name = {s.name: s for s in updated}

    changes = []

    for service in original:

        if service.name not in updated_by_name:
            continue

        if service.action != updated_by_name[service.name].action:
            changes.append(ServiceWithTrustValueBasic.from_service(updated_by_name[service.name]))

    return changes


def count_unstable_services(original: list[ServiceWithNegotiationData],
                            updated: list[ServiceWithNegotiationData]) -> int:
    """
    Count the number of services in `updated` whose action changed, i.e., the higher the worst
    """

    updated_by_name = {
        s.name: s
        for s in updated
    }

    unstable_services = 0

    for service in original:
        updated_service = updated_by_name.get(service.name)
        if updated_service is None:
            unstable_services += 1
        else:
            if service.action != updated_service.action:
                unstable_services += 1

    return unstable_services


def count_changed_actions(original: list[ServiceWithNegotiationData],
                          updated: list[ServiceWithNegotiationData]) -> int:
    """
    Count how many surviving services changed action.

    Services that left the application are ignored and contribute
    only to application stability.
    """

    updated_by_name = {s.name: s for s in updated}

    changes = 0

    for service in original:

        if service.name not in updated_by_name:
            continue
        # consider only the service that are still here
        if service.action != updated_by_name[service.name].action:
            # and that's it.
            changes += 1

    return changes
