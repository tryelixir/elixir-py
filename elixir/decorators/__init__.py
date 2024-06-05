from typing import Optional


from elixir.decorators.base import (
    aentity_class,
    aentity_method,
    entity_class,
    entity_method,
)


def observe(name: Optional[str] = None, method_name: Optional[str] = None):
    if method_name is None:
        return entity_method(name=name)
    else:
        return entity_class(name=name, method_name=method_name)


# Async Decorators
def aobserve(name: Optional[str] = None, method_name: Optional[str] = None):
    if method_name is None:
        return aentity_method(name=name)
    else:
        return aentity_class(name=name, method_name=method_name)
