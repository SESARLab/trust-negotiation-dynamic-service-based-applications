import enum
from dataclasses import dataclass


class Cardinality(enum.Enum):
    EXISTS = 'EXISTS'
    FORALL = 'FORALL'


@dataclass(frozen=True)
class GenerationProfileSetting:
    bad_probability: float
    avg_probability: float
    good_probability: float


@dataclass(frozen=True)
class GenerationRequirementValueSetting:
    proba_bad_avg: float
    proba_avg_good: float
    proba_bad_good: float



@dataclass(frozen=True)
class GenerationCardinalitySetting:
    exists_probability: float
    forall_probability: float


@dataclass(frozen=True)
class GenerationRequirementSettings:
    policy_probabilities: list[float]
    requirement_probabilities: GenerationRequirementValueSetting
    cardinality_probabilities: GenerationCardinalitySetting


@dataclass(frozen=True)
class GenerationChangeSetting:
    event_probability: float
    attribute_probability: float


@dataclass(frozen=True)
class ExperimentSetting:
    name: str

    profile: GenerationProfileSetting
    requirements: GenerationRequirementSettings
    changes: GenerationChangeSetting


