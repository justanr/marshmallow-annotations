from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple, Union
from uuid import UUID

from marshmallow import fields
from marshmallow.base import FieldABC, SchemaABC

from ._compat import _get_base
from .base import AbstractConverter, ConfigOptions, FieldFactory, TypeRegistry
from .exceptions import AnnotationConversionError


def _is_generic(typehint: type) -> bool:
    # this *could* be isinstance(typehint, (Generic, _GenericAlias)) but
    # this works out better given that __origin__ isn't likely to go away
    # the way _GenericAlias might
    return getattr(typehint, "__origin__", None) is not None


def field_factory(field: FieldABC) -> FieldFactory:
    """
    Maps a marshmallow field into a field factory
    """

    def _(
        converter: AbstractConverter, subtypes: Tuple[type], opts: ConfigOptions
    ) -> FieldABC:
        return field(**opts)

    _.__name__ = f"{field.__name__}FieldFactory"
    return _


def scheme_factory(scheme_name: str) -> FieldFactory:
    """
    Maps a scheme or scheme name into a field factory
    """

    def _(
        converter: AbstractConverter, subtypes: Tuple[type], opts: ConfigOptions
    ) -> FieldABC:
        return fields.Nested(scheme_name, **opts)

    _.__name__ = f"{scheme_name}FieldFactory"
    _.__is_scheme__ = True  # type: ignore
    return _


def _list_converter(
    converter: AbstractConverter, subtypes: Tuple[type], opts: ConfigOptions
) -> FieldABC:
    if converter.is_scheme(subtypes[0]):
        opts["many"] = True
        return converter.convert(subtypes[0], opts)
    sub_opts = opts.pop("_interior", {})
    return fields.List(converter.convert(subtypes[0], sub_opts), **opts)


class DefaultTypeRegistry(TypeRegistry):
    """
    Default implementation of :class:`~marshmallow_annotations.base.TypeRegistry`.

    Provides default mappings of:

    - bool -> fields.Boolean
    - date -> fields.Date
    - datetime -> fields.DateTime
    - Decimal -> fields.Decimal
    - float -> fields.Float
    - int -> fields.Integer
    - str -> fields.String
    - time -> fields.Time
    - timedelta -> fields.TimeDelta
    - UUID -> fields.UUID
    - dict -> fields.Dict
    - typing.Dict -> fields.Dict

    As well as a special factory for typing.List[T] that will generate either
    fields.List or fields.Nested
    """

    _registry = {
        k: field_factory(v)
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
            UUID: fields.UUID,
            dict: fields.Dict,
            Dict: fields.Dict,
        }.items()
    }

    # py36, py37 compatibility, register both out of praticality
    _registry[List] = _list_converter
    _registry[list] = _list_converter

    def __init__(self, registry: Dict[type, FieldFactory] = None) -> None:
        if registry is None:
            registry = {}

        self._registry = {**self._registry, **registry}

    def register(self, target: type, constructor: FieldFactory) -> None:
        self._registry[target] = constructor

    def get(self, target: type) -> FieldFactory:
        converter = self._registry.get(target)
        if converter is None and _is_generic(target):
            converter = self._registry.get(_get_base(target))

        if converter is None:
            raise AnnotationConversionError(f"No field factory found for {target!r}")
        return converter

    def register_field_for_type(self, target: type, field: FieldABC) -> None:
        self.register(target, field_factory(field))

    def register_scheme_factory(
        self, target: type, scheme_or_name: Union[str, SchemaABC]
    ) -> None:
        self.register(target, scheme_factory(scheme_or_name))

    def has(self, target: type) -> bool:
        return target in self._registry


registry = DefaultTypeRegistry()
