from typing import overload, Union
from abc import ABC,abstractmethod

from JedoxPy.Objects.Dimension import Dimension

class RuleTemplate(ABC):
    """ Base class for all the rule templates"""

    @abstractmethod
    def to_payload(self) -> dict:
        pass

    @abstractmethod
    def validate(self) -> None:
        pass

    #@abstractmethod


class RuleTemplateDimElementLike(RuleTemplate):

    def __init__(self, dimension: Dimension, pattern: str):
        self.dimension = dimension
        self.pattern = pattern

    def to_payload(self) -> dict:
        return {
            "name": "Dimension element like",
            "parameters": {
                "Dimension": self.dimension.name,
                "Pattern": self.pattern
            }
        }

    def validate(self) -> None:
        if not self.dimension or not self.pattern:
            raise ValueError("Both dimension and pattern are required")

    def check_params(self):
        pass


class RuleTemplateDimElementLikeList(RuleTemplate):

    def __init__(self, dimension: Dimension, pattern: str):
        self.dimension = dimension
        self.pattern = pattern

    def to_payload(self) -> dict:
        return {
            "name": "Dimension element like",
            "parameters": {
                "Dimension": self.dimension.name,
                "Pattern": self.pattern
            }
        }

    def validate(self) -> None:
        pass


class RuleTemplateDimElementLikeAttribute(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateDimElementLikeAttributeList(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateActualMonths(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateStaticFormatString(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateDimensionFormatString(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateKpiCalculation(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateKpiCalculationByVersion(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateAttributeLike(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateInitialMonths(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateGlobalSubsetElement(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateGlobalSubsetElementList(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateDimElementLikeGroupByOne(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateDimElementLikeGroupByTwo(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass


class RuleTemplateDimElementLikeGroupByThree(RuleTemplate):

    def to_payload(self) -> dict:
        pass

    def validate(self) -> None:
        pass