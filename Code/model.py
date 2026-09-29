from dataclasses import dataclass

import numpy as np

import settings_model


@dataclass
class TrustAttribute:
    value: float | int | str
    is_certified: bool

    def __post_init__(self):
        # fixes for numpy-related extraction.
        if type(self.value) is not int and not isinstance(self.value, str):
            # if str, stay as is.
            self.value = int(self.value)
        if type(self.is_certified) is not bool:
            self.is_certified = bool(self.is_certified)


@dataclass(frozen=True)
class TrustAttributeChange:
    """

    Attributes:
        - index : int
        - new_value : float | int | str
    """
    index: int # the index
    new_value: float| int | str


@dataclass(frozen=True)
class ChangeSet:
    """
    A set of changes applied to the trust attributes of a service *at once*.

    Attributes:
        changes: list[TrustAttributeChange]
    """
    changes: tuple[TrustAttributeChange, ...]


@dataclass(frozen=True)
class Policy:
    policy: tuple[float, ...]


@dataclass#(frozen=True)
class TrustRequirement:
    range: tuple[float | int | str, float | int] | set[float| str]
    cardinality: settings_model.Cardinality
    is_certified: bool

    def __post_init__(self):
        def map_range(x):
            if isinstance(x, np.floating):
                return float(x)
            elif isinstance(x, np.integer):
                return int(x)
            return x

        mapped_range = map(map_range, self.range)
        if isinstance(self.range, set):
            self.range = set(mapped_range )
        else:
            # if a tuple, check that it's not a string, because we can't manage it.
            if isinstance(self.range[0], str) or isinstance(self.range[1], str):
                raise ValueError('requirement cant be a tuple of str, only set is supported for str')
            if not len(self.range) == 2:
                raise ValueError(f'requirement as tuple must be of length 2, got: {len(self.range)}')
            self.range = tuple(mapped_range)
        if not isinstance(self.is_certified, bool):
            self.is_certified = bool(self.is_certified)


def get_action_from(trust_value: float, policy: Policy) -> int:
    """
    Returns a "mnemonic" action given the trust value.
    """
    for i, threshold in enumerate(policy.policy):
        if trust_value < threshold:
            return i - 1

    return len(policy.policy) - 1


def worsened(old_tv: float, new_tv: float, policy: Policy) -> bool:
    return get_action_from(new_tv, policy) <  get_action_from(old_tv, policy)


@dataclass
class Service:
    name: str
    policy: Policy
    attributes: list[TrustAttribute]
    requirements: list[TrustRequirement]

    def __eq__(self, value: object, /) -> bool:
        return isinstance(value, Service) and self.name == value.name

    def get_action_from(self, trust_value: float) -> int:
        return get_action_from(trust_value=trust_value, policy=self.policy)

    def apply_change(self, change_set: ChangeSet):
        """
        Apply a ChangeSet.
        """

        for change in change_set.changes:
            self.attributes[change.index] = TrustAttribute(
                value=change.new_value,
                is_certified=self.attributes[change.index].is_certified
            )


@dataclass
class ServiceWithNegotiationData(Service):
    _trust_value: float
    _action: int

    @classmethod
    def from_service(cls, s: Service, trust_value: float) -> "ServiceWithNegotiationData":
        return ServiceWithNegotiationData(
            name=s.name,
            policy=s.policy,
            attributes=s.attributes,
            requirements=s.requirements,
            _trust_value=trust_value,
            _action=get_action_from(trust_value=trust_value, policy=s.policy)
        )

    @property
    def action(self) -> int:
        return self._action

    def set_action(self, action: int, force: bool = False):
        """
        Explicit modification of an action.

        When `force` is `True`, the action is modified without checking consistency with the policy.
        This is needed because in dynamic trust we "reject" improvements on the actions, while
        normally the action is automatically set on the basis of the trust value and policy.
        """
        correct_action = get_action_from(trust_value=self._trust_value, policy=self.policy)
        if correct_action != action and not force:
            raise ValueError('cannot update action when not forced')
        self._action = action

    @property
    def trust_value(self) -> float:
        return self._trust_value

    def get_action(self):
        return self.get_action_from(trust_value=self._trust_value)

    def set_trust_value(self, trust_value: float) -> None:
        self._trust_value = trust_value
        self._action = get_action_from(trust_value=trust_value, policy=self.policy)


@dataclass
class SotaServiceWithNegotiationData(Service):
    # raw pairwise trust values [service name -> value].
    trust_vector: dict[str, float]
    # thresholded trust values.
    compatibility_vector: dict[str, bool]
    # whether the service belongs to the selected coalition.
    # I.e., it will be the lowest action.
    _action: int
    _trust_value: float

    @classmethod
    def from_service(cls, s: Service,
                     trust_vector: dict[str, float],
                     compatibility_vector: dict[str, bool],
                     enters: bool
                     ) -> "SotaServiceWithNegotiationData":
        vals = [v for k, v in trust_vector.items() if k != s.name]

        return SotaServiceWithNegotiationData(
            name=s.name,
            policy=s.policy,
            attributes=s.attributes,
            requirements=s.requirements,
            trust_vector=trust_vector,
            compatibility_vector=compatibility_vector,
            _action=-1 if not enters else 0, # coherent with how we represent actions.
            _trust_value=float(np.mean(vals)) if len(vals) > 0 else 0.0,
        )

    @property
    def action(self) -> int:
        return self._action

    @property
    def trust_value(self) -> float:
        return self._trust_value
