from datetime import date, datetime, time, timedelta
from decimal import Decimal
from functools import wraps
from types import MappingProxyType
from typing import GenericMeta, List, Union, get_type_hints
from uuid import UUID

from marshmallow import Schema, fields
from marshmallow.base import SchemaABC
from marshmallow.class_registry import get_class as get_scheme
from marshmallow.exceptions import MarshmallowError
from marshmallow.schema import SchemaMeta

NoneType = type(None)
_UNION_TYPE = type(Union)


class MarshmallowAnnotationError(MarshmallowError):
    pass


class AnnotationConversionError(MarshmallowAnnotationError):
    pass


def default_field_constructor(field):

    def _(converter, subtypes, k):
        return field(**k)

    _.__name__ = f"{field.__name__}FieldConstructor"
    return _


def default_scheme_constructor(scheme_name):

    def _(converter, subtypes, k):
        return fields.Nested(scheme_name, **k)

    _.__name__ = f"{scheme_name}FieldConstructor"
    return _


def _list_converter(converter, subtypes, k):
    return fields.List(converter(subtypes[0]), **k)


class TypeRegistry:
    _registry = {
        k: default_field_constructor(v)
        for k, v in {
            bool: fields.Boolean,
            date: fields.Date,
            datetime: fields.DateTime,
            Decimal: fields.Decimal,
            float: fields.Float,
            int: fields.Integer,
            str: fields.String,
            time: fields.Time,
            timedelta: fields.TimeDelta,
            UUID: fields.UUID
        }.items()
    }

    _registry[List] = _list_converter

    registry = MappingProxyType(_registry)

    @classmethod
    def register(cls, type, field_constructor):
        cls._registry[type] = field_constructor

    @classmethod
    def field_constructor(cls, type):

        def field_constructor(constructor):
            cls.register(type, constructor)
            return constructor

        return field_constructor

    @classmethod
    def from_type(cls, type):
        converter = cls._registry.get(type)
        if converter is None:
            raise AnnotationConversionError(
                f'No field factory found for {type!r}'
            )
        return converter

    @classmethod
    def register_field_for_type(cls, type, field):
        cls.register(type, default_field_constructor(field))

    @classmethod
    def register_scheme_constructor(cls, type, scheme_or_name):
        cls.register(type, default_scheme_constructor(scheme_or_name))




def _is_optional(typehint):
    # only supports single type optionals/unions
    # as for the implementation... look, don't ask me
    return _UNION_TYPE in type(typehint).__mro__ and len(
        typehint.__args__
    ) == 2 and typehint.__args__[1] is NoneType


class BaseConverter:

    def __init__(self, scheme, *, registry=TypeRegistry):
        self.registry = TypeRegistry
        self.scheme = scheme

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

    def _exists_on_scheme(self, name):
        if self.scheme is None:
            return False

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

    def __call__(self, typehint, **k):
        return self._field_from_typehint(typehint, k)

    def _get_type_hints(self, item):
        hints = {}

        for parent in item.__mro__[::-1]:
            hints.update(get_type_hints(parent))

        return hints

    def convert(self, name, typehint, **kwargs):
        opts = {**self._get_meta_options(name), **kwargs}
        return self._field_from_typehint(typehint, opts)

    def convert_all(self, type, ignore=frozenset()):
        return {
            k: self.convert(k, v)
            for k, v in self._get_type_hints(type).items() if k not in ignore
        }


class AnnotationSchemaMeta(SchemaMeta):

    @staticmethod
    def __new__(mcls, name, bases, attrs, **k):
        cls = super().__new__(mcls, name, bases, attrs)
        meta = getattr(cls, 'Meta', None)
        cls._register_as_scheme_for_target(meta)
        return cls

    @classmethod
    def get_declared_fields(
            mcls, klass, cls_fields, inherited_fields, dict_cls
    ):
        fields = super().get_declared_fields(
            klass, cls_fields, inherited_fields, dict_cls
        )

        meta = getattr(klass, 'Meta', None)

        if not meta:
            return fields

        target = getattr(meta, 'target', None)

        if target is None:
            return fields

        converter_factory = getattr(meta, 'converter', BaseConverter)

        # weeeee circular references!
        meta.converter = converter = converter_factory(klass)

        # ignore anything explicitly declared on this scheme
        # or any parent scheme
        ignore = fields.keys()
        fields.update(converter.convert_all(target, ignore))

        return fields

    @classmethod
    def _register_as_scheme_for_target(cls, meta):
        if meta is None:
            return

        should_register = getattr(meta, 'register_as_scheme', False)
        target = getattr(meta, 'target', None)

        if should_register and target:
            TypeRegistry.register_scheme_constructor(target, cls)


class AnnotationSchema(Schema, metaclass=AnnotationSchemaMeta):
    pass
