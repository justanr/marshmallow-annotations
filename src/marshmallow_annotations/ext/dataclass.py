from typing import AbstractSet, Tuple, Callable

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

_DATACLASS_METADATA_KEY = "marshmallow-annotations"


def _should_include_default(field: Field) -> bool:
    if not field.init:
        return False

    return field.default != MISSING


def _get_field(target, name: str) -> Field:
    return target.__dataclass_fields__[name]


def _has_default(field: Field) -> bool:
    return field.default != MISSING or field.default_factory != MISSING


def _initvar_converter(
    converter: BaseConverter, subtype: Tuple[type], opts: ConfigOptions
) -> FieldABC:
    if 'initvar-typehint' not in opts.get("metadata", {}):
        raise ValueError("use field(metadata=initvar_typehint(<typehint)) "
                         "or field(..., metadata={**other_metadata, **initvar_typehint(<typehint>)})")
    real_typehint = opts["metadata"]["initvar-typehint"]
    real_field_constructor = converter.registry.get(real_typehint)
    return real_field_constructor(converter, real_typehint, opts)


class DataclassConverter(BaseConverter):
    def __init__(self, *, registry: TypeRegistry) -> None:
        super().__init__(registry=registry)
        self._register_initvar_conversion()

    def _get_field_defaults(self, target):
        return {
            k: v.default
            for k, v in target.__dataclass_fields__.items()
            if _should_include_default(v)
        }

    def _preprocess_typehint(self, typehint, kwargs, field_name, target):
        field = _get_field(target, field_name)
        kwargs["metadata"] = field.metadata.get(_DATACLASS_METADATA_KEY)
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


def initvar_typehint(typehint: type):
    return {_DATACLASS_METADATA_KEY: {"initvar-typehint": typehint}}


def validator(validation_fn: Callable):
    return
