import dataclasses
from typing import Any

from model import Service, ChangeSet
from trust_dynamic import dynamic_trust
from trust_negotiation import negotiation


def get_changed_service_name_from(services: list[Service], name: str) -> int:
    for i, service in enumerate(services):
        if service.name == name:
            return i
    raise ValueError(f'Service {name} not found')


def execute_walkthrough(services: list[Service], changes: list[tuple[str, ChangeSet]]) -> dict[str, Any]:
    result = {}
    change_objs = []

    # 1. do the negotiation
    negotiation_result = negotiation(services)
    # and report the included/excluded services.
    result['included'] = [{'name': s.name, 'trust_value': s.trust_value, 'action': s.action} for s in negotiation_result.included]
    result['excluded'] = [{'name': s.name, 'trust_value': s.trust_value, 'action': s.action} for s in negotiation_result.excluded]
    # result['len(included)'] = len(result['included'])
    # result['len(excluded)'] = len(result['excluded'])

    current_system = negotiation_result.included

    # now, apply the change.
    for change_id, (changed_service_name, change_set) in enumerate(changes):
        dynamic_trust_result = dynamic_trust(
            system=current_system,
            changed_service_index=get_changed_service_name_from(current_system, changed_service_name),
            change_set=change_set,
            debug=True,
        )
        # begin to add info.
        change_obj: dict[str, Any] = { # forced type to avoid issues with the annoying type-checker.
            'index': change_id,
            'changed': {
                'service_name': changed_service_name,
                'trust_attributes': [
                    {
                        'attribute_index': change.index,
                        'new_value': change.new_value
                    } for change in change_set.changes
                ],
            },
            'relevant': dynamic_trust_result.relevant,
        }
        # now, here, the change may be irrelevant.
        if dynamic_trust_result.relevant:
            # need to add this because debug_planning is normally None except when explicitly specified.
            # (it's just for type-checking)
            assert dynamic_trust_result.debug_planning is not None
            assert dynamic_trust_result.debug_planning.s_keep is not None
            assert dynamic_trust_result.debug_planning.s_eviction is not None
            change_obj.update({
                'metrics': {
                    'application_stability': dynamic_trust_result.application_stability,
                    'service_stability': dynamic_trust_result.service_stability,
                    'action_stability': dynamic_trust_result.action_stability,
                },
                'planning': {
                    'decision': dynamic_trust_result.debug_planning.decision,
                    'scenario_keep': dataclasses.asdict(dynamic_trust_result.debug_planning.s_keep),
                    'scenario_evict': dataclasses.asdict(dynamic_trust_result.debug_planning.s_eviction),
                },
                'after_change': {
                    'included': [{'name': s.name, 'trust_value': s.trust_value, 'action': s.action}
                                 for s in dynamic_trust_result.debug_planning.simulation.included],
                    'excluded': [{'name': s.name, 'trust_value': s.trust_value, 'action': s.action}
                                 for s in dynamic_trust_result.debug_planning.simulation.excluded],
                }
            })

            current_system = dynamic_trust_result.debug_planning.simulation.included

        change_objs.append(change_obj)
    result['changes'] = change_objs
    return result
