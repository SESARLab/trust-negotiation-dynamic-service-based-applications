from model import Policy
from settings_model import ExperimentSetting, GenerationProfileSetting, GenerationRequirementSettings, \
    GenerationRequirementValueSetting, GenerationCardinalitySetting, GenerationChangeSetting

POLICY_LOOSE = Policy(policy=(0.3, 0.6))
POLICY_STRICT = Policy(policy=(0.6, 0.9))

TRUST_ATTRIBUTE_VALUE_BAD = 0
TRUST_ATTRIBUTE_VALUE_AVG = 1
TRUST_ATTRIBUTE_VALUE_GOOD = 2
ALL_TRUST_ATTRIBUTE_VALUES = [TRUST_ATTRIBUTE_VALUE_BAD, TRUST_ATTRIBUTE_VALUE_AVG, TRUST_ATTRIBUTE_VALUE_GOOD]
TRUST_REQUIREMENT_BAD_AVG = (TRUST_ATTRIBUTE_VALUE_BAD, TRUST_ATTRIBUTE_VALUE_AVG)
TRUST_REQUIREMENT_AVG_GOOD = (TRUST_ATTRIBUTE_VALUE_AVG, TRUST_ATTRIBUTE_VALUE_GOOD)
TRUST_REQUIREMENT_BAD_GOOD = (TRUST_ATTRIBUTE_VALUE_BAD, TRUST_ATTRIBUTE_VALUE_GOOD)

N_SERVICES = [10, 25, 50, 100]
N_TRUST_ATTRIBUTES = [10, 25, 50, 100]
N_EXECUTIONS = 5
N_CHANGES = 100

# different profile settings that define the probabilities of choosing
# a given trust attribute value for a trust attribute
SETTINGS_PROFILE = [
    # G1.*.*
    GenerationProfileSetting(
        bad_probability=1 / 3,
        avg_probability=1 / 3,
        good_probability=1 / 3
    ),
    # G2.*.*
    GenerationProfileSetting(
        bad_probability=0.5,
        avg_probability=0.25,
        good_probability=0.25
    ),
    # G3.*.*
    GenerationProfileSetting(
        bad_probability=0.25,
        avg_probability=0.5,
        good_probability=0.25
    ),
    # G4.*.*
    GenerationProfileSetting(
        bad_probability=0.25,
        avg_probability=0.25,
        good_probability=0.5
    )
]

# different requirement settings that define the probabilities of choosing
# a given trust requirement for a trust attribute
SETTINGS_REQUIREMENTS = [
    # G*.1.*
    GenerationRequirementSettings(
        policy_probabilities=[0.5, 0.5],
        requirement_probabilities=GenerationRequirementValueSetting(
            proba_bad_avg=1 / 3,
            proba_avg_good=1 / 3,
            proba_bad_good=1 / 3
        ),
        cardinality_probabilities=GenerationCardinalitySetting(
            exists_probability=0.5,
            forall_probability=0.5
        )
    ),
    # G*.2.
    GenerationRequirementSettings(
        policy_probabilities=[2 / 3, 1 / 3],
        requirement_probabilities=GenerationRequirementValueSetting(
            proba_bad_avg=2 / 3,
            proba_avg_good=(1 / 3) / 2,
            proba_bad_good=(1 / 3) / 2
        ),
        cardinality_probabilities=GenerationCardinalitySetting(
            exists_probability=2 / 3,
            forall_probability=1 / 3
        )
    ),
    # G*.3.*
    GenerationRequirementSettings(
        policy_probabilities=[1 / 3, 2 / 3],
        requirement_probabilities=GenerationRequirementValueSetting(
            proba_bad_avg=(1 / 3) / 2,
            proba_avg_good=2 / 3,
            proba_bad_good=(1 / 3) / 2
        ),
        cardinality_probabilities=GenerationCardinalitySetting(
            exists_probability=2 / 3,
            forall_probability=1 / 3
        )
    )
]

SETTINGS_CHANGE = [
    # G*.*1
    GenerationChangeSetting(
        event_probability=0.25,
        attribute_probability=0.25
    ),
    # G*.*.2
    GenerationChangeSetting(
        event_probability=0.25,
        attribute_probability=0.75
    ),
    # G*.*.3
    GenerationChangeSetting(
        event_probability=0.75,
        attribute_probability=0.25
    )
]

def get_settings() -> list[ExperimentSetting]:
    settings = []

    for profile_idx, profile in enumerate(SETTINGS_PROFILE, start=1):
        for req_idx, reqs in  enumerate(SETTINGS_REQUIREMENTS, start=1):
            for change_idx, change in enumerate(SETTINGS_CHANGE, start=1):
                settings.append(
                    ExperimentSetting(
                        name=f"G{profile_idx}.{req_idx}.{change_idx}",
                        profile=profile,
                        requirements=reqs,
                        changes=change
                    )
                )
    return settings
