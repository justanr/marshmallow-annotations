from abc import ABC, abstractmethod
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Callable, Dict, List, Tuple, Union
from uuid import UUID

from marshmallow import fields
from marshmallow.base import FieldABC, SchemaABC

from .base import AbstractConverter, ConfigOptions, FieldConstructor, TypeRegistry
from .exceptions import AnnotationConversionError


def default_field_constructor(field: FieldABC) -> FieldConstructor:

    def _(
        converter: AbstractConverter, subtypes: Tuple[type], k: ConfigOptions
    ) -> FieldABC:
        return field(**k)

    _.__name__ = f"{field.__name__}FieldConstructor"
    return _


def default_scheme_constructor(scheme_name: str) -> FieldConstructor:

    def _(
        converter: AbstractConverter, subtypes: Tuple[type], k: ConfigOptions
    ) -> FieldABC:
        return fields.Nested(scheme_name, **k)

    _.__name__ = f"{scheme_name}FieldConstructor"
    return _


def _list_converter(
    converter: AbstractConverter, subtypes: Tuple[type], k: ConfigOptions
) -> FieldABC:
    return fields.List(converter.convert(subtypes[0]), **k)


class DefaultTypeRegistry(TypeRegistry):
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

    def __init__(self, registry: Dict[type, FieldConstructor] = None) -> None:
        if registry is None:
            registry = {}

        self._registry = {**self._registry, **registry}

    def register(self, target: type, constructor: FieldConstructor) -> None:
        self._registry[target] = constructor

    def field_constructor(
        self, target: type
    ) -> Callable[[FieldConstructor], FieldConstructor]:

        def field_constructor(constructor: FieldConstructor) -> FieldConstructor:
            self.register(target, constructor)
            return constructor

        return field_constructor

    def get(self, target: type) -> FieldConstructor:
        converter = self._registry.get(target)
        if converter is None:
            raise AnnotationConversionError(f"No field factory found for {target!r}")
        return converter

    def register_field_for_type(self, target: type, field: FieldABC) -> None:
        self.register(target, default_field_constructor(field))

    def register_scheme_constructor(
        self, target: type, scheme_or_name: Union[str, SchemaABC]
    ):
        self.register(target, default_scheme_constructor(scheme_or_name))

    def __contains__(self, target: type) -> bool:
        return target in self._registry
registry = DefaultTypeRegistry()
