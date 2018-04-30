from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Callable, Dict, List, Tuple, Union
from uuid import UUID

from marshmallow import fields
from marshmallow.base import FieldABC, SchemaABC

from .base import AbstractConverter, ConfigOptions, FieldFactory, TypeRegistry
from .exceptions import AnnotationConversionError


def default_field_factory(field: FieldABC) -> FieldFactory:
    """
    Maps a marshmallow field into a field factory
    """

    def _(
        converter: AbstractConverter, subtypes: Tuple[type], opts: ConfigOptions
    ) -> FieldABC:
        return field(**opts)

    _.__name__ = f"{field.__name__}FieldFactory"
    return _


def default_scheme_factory(scheme_name: str) -> FieldFactory:
    """
    Maps a scheme or scheme name into a field factory
    """

    def _(
        converter: AbstractConverter, subtypes: Tuple[type], opts: ConfigOptions
    ) -> FieldABC:
        return fields.Nested(scheme_name, **opts)

    _.__name__ = f"{scheme_name}FieldFactory"
    return _


def _list_converter(
    converter: AbstractConverter, subtypes: Tuple[type], opts: ConfigOptions
) -> FieldABC:
    return fields.List(converter.convert(subtypes[0]), **opts)


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

    As well typing.List[T] -> fields.List

    Uses a dictionary as its backing store.
    """

    _registry = {
        k: default_field_factory(v)
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
        }.items()
    }

    _registry[List] = _list_converter

    def __init__(self, registry: Dict[type, FieldFactory] = None) -> None:
        if registry is None:
            registry = {}

        self._registry = {**self._registry, **registry}

    def register(self, target: type, constructor: FieldFactory) -> None:
        self._registry[target] = constructor

    def get(self, target: type) -> FieldFactory:
        converter = self._registry.get(target)
        if converter is None:
            raise AnnotationConversionError(f"No field factory found for {target!r}")
        return converter

    def register_field_for_type(self, target: type, field: FieldABC) -> None:
        self.register(target, default_field_factory(field))

    def register_scheme_factory(
        self, target: type, scheme_or_name: Union[str, SchemaABC]
    ) -> None:
        self.register(target, default_scheme_factory(scheme_or_name))

    def has(self, target: type) -> bool:
        return target in self._registry


registry = DefaultTypeRegistry()
