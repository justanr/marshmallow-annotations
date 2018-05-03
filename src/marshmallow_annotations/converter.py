from typing import _ClassVar  # type: ignore
from typing import AbstractSet, Union, get_type_hints

from marshmallow import fields

from .base import (
    AbstractConverter,
    ConfigOptions,
    GeneratedFields,
    NamedConfigs,
    TypeRegistry,
)
from .registry import registry

NoneType = type(None)
_UNION_TYPE = type(Union)


def _is_optional(typehint):
    # only supports single type optionals/unions
    # as for the implementation... look, don't ask me
    return (
        _UNION_TYPE in type(typehint).__mro__  # noqa
        and len(typehint.__args__) == 2  # noqa
        and typehint.__args__[1] is NoneType  # noqa
    )


def _is_class_var(typehint):
    try:
        return isinstance(typehint, _ClassVar)
    except TypeError:  # pragma: no branch
        return False


def should_include(typehint):
    return not _is_class_var(typehint)


class BaseConverter(AbstractConverter):
    """
    Default implementation of :class:`~marshmallow_annotations.base.AbstractConverter`.

    Handles parsing types for type hints and mapping those type hints into
    marshmallow field instances by way of a
    :class:`~marshmallow_annotations.base.TypeRegistry` instance.
    """

    def __init__(self, *, registry: TypeRegistry = registry) -> None:
        self.registry = registry

    def convert(self, typehint: type, opts: ConfigOptions = None) -> fields.FieldABC:
        opts = opts if opts is not None else {}
        return self._field_from_typehint(typehint, opts)

    def convert_all(
        self,
        target: type,
        ignore: AbstractSet[str] = frozenset([]),  # noqa
        configs: NamedConfigs = None,
    ) -> GeneratedFields:
        configs = configs if configs is not None else {}
        return {
            k: self.convert(v, configs.get(k, {}))
            for k, v in self._get_type_hints(target).items()
            if k not in ignore and should_include(v)
        }

    def is_scheme(self, typehint: type) -> bool:
        constructor = self.registry.get(typehint)
        return getattr(constructor, "__is_scheme__", False)

    def _field_from_typehint(self, typehint, kwargs=None):
        # need that immutable dict in the stdlib pls
        kwargs = kwargs if kwargs is not None else {}

        # sane defaults
        allow_none = False
        required = True

        if _is_optional(typehint):
            allow_none = True
            required = False
            typehint = typehint.__args__[0]

        # set this after optional check
        subtypes = getattr(typehint, "__args__", ())

        if subtypes != ():
            typehint = typehint.__base__

        kwargs.setdefault("allow_none", allow_none)
        kwargs.setdefault("required", required)

        field_constructor = self.registry.get(typehint)
        return field_constructor(self, subtypes, kwargs)

    def _get_type_hints(self, item):
        hints = {}
        for parent in item.__mro__[::-1]:
            hints.update(get_type_hints(parent))
        return hints
