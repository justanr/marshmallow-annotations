from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Dict, Set, Union, _ClassVar, get_type_hints

from marshmallow import fields

from .base import AbstractConverter, Options, TypeRegistry
from .exceptions import AnnotationConversionError, MarshmallowAnnotationError
from .registry import registry

NoneType = type(None)
_UNION_TYPE = type(Union)


def _is_optional(typehint):
    # only supports single type optionals/unions
    # as for the implementation... look, don't ask me
    return _UNION_TYPE in type(typehint).__mro__ and len(
        typehint.__args__
    ) == 2 and typehint.__args__[1] is NoneType


def _is_class_var(typehint):
    try:
        return isinstance(typehint, _ClassVar)
    except:
        return False


def should_include(typehint):
    return not _is_class_var(typehint)


class BaseConverter:

    def __init__(self, scheme, *, registry: TypeRegistry=registry) -> None:
        self.registry = TypeRegistry
        self.scheme = scheme

    def convert(self, typehint: type, **k: Options) -> fields.FieldABC:
        return self._field_from_typehint(typehint, k)

    def convert_with_options(
            self, name: str, typehint: type, kwargs: Options
    ) -> fields.FieldABC:
        opts = {**self._get_meta_options(name), **kwargs}
        return self._field_from_typehint(typehint, opts)

    def convert_all(self, target: type, ignore: Set[str]=frozenset([])
                    ) -> Dict[str, fields.FieldABC]:
        return {
            k: self.convert_with_options(k, v)
            for k, v in self._get_type_hints(target).items()
            if k not in ignore and should_include(v)
        }

    def _field_from_typehint(self, typehint, kwargs=None):
        # need that immutable dict in the stdlib pls
        kwargs = kwargs if kwargs is not None else {}

        # sane defaults
        allow_none = False
        required = True

        if _is_optional(typehint):
            allow_none = True
            typehint = typehint.__args__[0]

        # set this after optional check
        subtypes = getattr(typehint, '__args__', ())

        if subtypes != ():
            typehint = typehint.__base__

        kwargs.setdefault('allow_none', allow_none)
        kwargs.setdefault('required', required)

        field_constructor = self.registry.from_type(typehint)
        return field_constructor(self, subtypes, kwargs)

    def _get_meta_options(self, name):
        if self.scheme is None:
            return {}

        parent_meta_options = self._visit_parent_metas(
            lambda meta: getattr(meta, name, None)
        )

        return parent_meta_options or {}

    def _visit_parent_metas(self, f):
        for parent in self.scheme.__mro__:
            meta = getattr(parent, 'Meta', None)
            if meta is not None:
                result = f(meta)
                if result:
                    return result

    def _get_type_hints(self, item):
        hints = {}

        for parent in item.__mro__[::-1]:
            hints.update(get_type_hints(parent))
        return hints
