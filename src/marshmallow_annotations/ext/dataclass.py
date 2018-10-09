from typing import AbstractSet, Tuple

from dataclasses import MISSING, Field, InitVar, _FIELD_INITVAR
from marshmallow import missing, post_load
from marshmallow.base import FieldABC

from ..base import (
    AbstractConverter,
    ConfigOptions,
    GeneratedFields,
    NamedConfigs,
    TypeRegistry,
)
from ..exceptions import AnnotationConversionError
from ..scheme import AnnotationSchema, BaseConverter

__all__ = ("DataclassConverter", "DataclassSchema")


def _should_include_default(field: Field) -> bool:
    if not field.init:
        return False

    return field.default != MISSING


def _get_field(target, name: str) -> Field:
    return target.__dataclass_fields__[name]


def _has_default(field: Field) -> bool:
    return field.default != MISSING or field.default_factory != MISSING


def _initvar_converter(
    converter: AbstractConverter, subtype: Tuple[type], opts: ConfigOptions
) -> FieldABC:
    return converter.convert(subtype[0], opts)


class DataclassConverter(BaseConverter):
    def __init__(self, *, registry: TypeRegistry) -> None:
        super().__init__(registry=registry)
        self._register_initvar_conversion()

    def _get_field_defaults(self, target):
        return {
            k: v.default
            for k, v in target.__dataclass_fields__
            if _should_include_default(v)
        }

    def _preprocess_typehint(self, typehint, kwargs, field_name, target):
        field = _get_field(target, field_name)

        if _has_default(field):
            kwargs.setdefault("required", False)
            kwargs.setdefault("missing", missing)

    def _postprocess_typehint(self, typehint, kwargs, field_name, target):
        field = _get_field(target, field_name)

        if not field.init:
            kwargs["dump_only"] = True

    def _register_initvar_conversion(self):
        if not self.registry.has(InitVar):
            self.registry.register(InitVar, _initvar_converter)


class DataclassSchema(AnnotationSchema):
    class Meta:
        converter_factory = DataclassConverter

    @post_load
    def make_object(self, data):
        return self.opts.target(**data)
