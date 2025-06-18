from typing import overload
from JedoxPy.Objects.Enums import RuleTemplateType

from JedoxPy.Objects.Dimension import Dimension
from JedoxPy.Objects.RuleTemplate import *


@overload
def RuleTemplateQuery(template_type: RuleTemplateType.DIMENSION_ELEMENT_LIKE, *, dimension: Dimension, pattern: str) -> RuleTemplateDimElementLike: ...

@overload
def RuleTemplateQuery(template_type: RuleTemplateType.DIMENSION_ELEMENT_LIKE_LIST, *, dimension: Dimension, pattern: str) -> RuleTemplateDimElementLikeList: ...


def RuleTemplateQuery(template_type: RuleTemplateType, **kwargs) -> RuleTemplate:
    if template_type == RuleTemplateType.DIMENSION_ELEMENT_LIKE:
        return RuleTemplateDimElementLike(**kwargs)
    elif template_type == RuleTemplateType.DIMENSION_ELEMENT_LIKE_LIST:
        return RuleTemplateDimElementLikeList(**kwargs)
    else:
        raise ValueError(f"Unsupported rule template type: {template_type}")
