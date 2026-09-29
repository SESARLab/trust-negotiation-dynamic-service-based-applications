from dataclasses import dataclass

import numpy as np

from model import (
    Service,
    TrustAttribute,
    TrustRequirement, ChangeSet, TrustAttributeChange, Policy,
)
from settings_data import POLICY_LOOSE, POLICY_STRICT, TRUST_ATTRIBUTE_VALUE_BAD, TRUST_ATTRIBUTE_VALUE_AVG, \
    TRUST_ATTRIBUTE_VALUE_GOOD, TRUST_REQUIREMENT_BAD_AVG, TRUST_REQUIREMENT_AVG_GOOD, TRUST_REQUIREMENT_BAD_GOOD, \
    ALL_TRUST_ATTRIBUTE_VALUES
from settings_model import ExperimentSetting, Cardinality


@dataclass
class ExperimentalDataset:
    services: list[Service]


class DatasetGenerator:

    def __init__(self, setting: ExperimentSetting):
        self.setting = setting
        self.rng = np.random.default_rng()

    def _generate_attribute(self) -> TrustAttribute:
        return TrustAttribute(
            value=self.rng.choice(
                [
                    TRUST_ATTRIBUTE_VALUE_BAD,
                    TRUST_ATTRIBUTE_VALUE_AVG,
                    TRUST_ATTRIBUTE_VALUE_GOOD,
                ],
                p=[self.setting.profile.bad_probability,
                   self.setting.profile.avg_probability,
                   self.setting.profile.good_probability]),
            is_certified=self.rng.choice(
                [True, False],
                p=[0.5, 0.5]
            )
        )

    def _generate_requirement(self) -> TrustRequirement:
        return TrustRequirement(
            range=self.rng.choice(
                    [
                        TRUST_REQUIREMENT_BAD_AVG,
                        TRUST_REQUIREMENT_AVG_GOOD,
                        TRUST_REQUIREMENT_BAD_GOOD,
                    ],
                    p=[
                        self.setting.requirements.requirement_probabilities.proba_bad_avg,
                        self.setting.requirements.requirement_probabilities.proba_avg_good,
                        self.setting.requirements.requirement_probabilities.proba_bad_good
                    ]
                ),
            cardinality=Cardinality(self.rng.choice(
                [Cardinality.EXISTS.value, Cardinality.FORALL.value],
                p=[
                    self.setting.requirements.cardinality_probabilities.exists_probability,
                    self.setting.requirements.cardinality_probabilities.forall_probability
                ]
            )),
            is_certified=self.rng.choice([True, False], p=[0.5, 0.5])
        )

    def _generate_policy(self) -> Policy:
        return self.rng.choice(
            [POLICY_LOOSE, POLICY_STRICT],
            p=self.setting.requirements.policy_probabilities
        )

    def _generate_service(self, index: int, attributes_num: int) -> Service:
        attributes = [
            self._generate_attribute()
            for _ in range(attributes_num)
        ]

        requirements = [
            self._generate_requirement()
            for _ in range(attributes_num)
        ]

        return Service(
            name=f's{index}',
            policy=self._generate_policy(),
            attributes=attributes,
            requirements=requirements
        )

    def generate(self, n_services: int, n_trust_attributes: int) -> ExperimentalDataset:
        """
        Generate a dataset with the set of services.
        """
        services = [
            self._generate_service(
                index=i,
                attributes_num=n_trust_attributes
            )
            for i in range(n_services)
        ]

        return ExperimentalDataset(
            services=services
        )

    def generate_change_set(self, service: Service) -> ChangeSet:
        """
        Generate *one* change set for this service.
        """
        changes = []

        while len(changes) == 0:
            # for every attribute of the service, we determine whether it participates
            for i, attribute in enumerate(service.attributes):
                participates = self.rng.choice(
                        [True, False],
                        p=[self.setting.changes.attribute_probability,
                           1 - self.setting.changes.attribute_probability]
                    )
                if not participates:
                    continue
                # else, determines its new value.
                possible_values = [value for value in ALL_TRUST_ATTRIBUTE_VALUES if value != attribute.value]
                new_value = self.rng.choice(possible_values)
                changes.append(
                    TrustAttributeChange(
                        index=i,
                        new_value=int(new_value), # otherwise it's np.int64 and things get messed up
                    )
                )

        return ChangeSet(changes=tuple(changes))

    def change_occurs(self) -> bool:
        return self.rng.choice([True, False],
                               p=[
                                   self.setting.changes.event_probability,
                                  1-self.setting.changes.event_probability
                               ])

    def choose_changed_service(self, system: list[Service]) -> int:
        return self.rng.choice(len(system))
