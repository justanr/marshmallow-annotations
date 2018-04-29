from abc import ABC, abstractmethod
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Callable, List, Tuple, Union
from uuid import UUID

from marshmallow import fields
from marshmallow.base import FieldABC, SchemaABC

from .base import AbstractConverter, FieldConstructor, Options, TypeRegistry


def default_field_constructor(field: FieldABC) -> FieldConstructor:

    def _(converter: AbstractConverter, subtypes: Tuple[type], k: Options) -> FieldABC:
        return field(**k)

    _.__name__ = f"{field.__name__}FieldConstructor"
    return _


def default_scheme_constructor(scheme_name: str) -> FieldConstructor:

    def _(converter: AbstractConverter, subtypes: Tuple[type], k: Options) -> FieldABC:
        return fields.Nested(scheme_name, **k)

    _.__name__ = f"{scheme_name}FieldConstructor"
    return _


def _list_converter(
    converter: AbstractConverter, subtypes: Tuple[type], k: Options
) -> FieldABC:
    return fields.List(converter.convert(subtypes[0]), **k)


class DefaultTypeRegistry:
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
            UUID: fields.UUID,
        }.items()
    }

    _registry[List] = _list_converter

    def __init__(self, registry: Dict[str, FieldConstructor] = None) -> None:
        if registry is None:
            registry = {}

        self._registry = {**self._registry, **registry}

    def register(self, target: type, constructor: FieldConstructor) -> None:
        self._registry[type] = field_constructor

    def field_constructor(self, type: type) -> FieldConstructor:

        def field_constructor(constructor):
            self.register(type, constructor)
            return constructor

        return field_constructor

    def get(self, type: type) -> FieldConstructor:
        converter = self._registry.get(type)
        if converter is None:
            raise AnnotationConversionError(f"No field factory found for {type!r}")
        return converter

    def register_field_for_type(self, type: type, field: FieldABC) -> None:
        self.register(type, default_field_constructor(field))

    def register_scheme_constructor(
        self, type: type, scheme_or_name: Union[str, SchemaABC]
    ):
        self.register(type, default_scheme_constructor(scheme_or_name))


registry = DefaultTypeRegistry()
