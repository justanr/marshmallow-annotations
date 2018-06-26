"""Specialized components for Python 3.6 NamedTuple annotations."""

from typing import AbstractSet

import marshmallow

from .base import GeneratedFields, NamedConfigs
from .converter import should_include, BaseConverter
from .scheme import AnnotationSchema, AnnotationSchemaOpts


class NamedTupleConverter(BaseConverter):
    def convert_all(
        self,
        target: type,
        ignore: AbstractSet[str] = frozenset(),  # noqa
        configs: NamedConfigs = None,
    ) -> GeneratedFields:
        configs = configs if configs is not None else {}
        return {
            k: self.convert(v, {
                'missing': target._field_defaults.get(k),  # type: ignore
                **configs.get(k, {})})
            for k, v in self._get_type_hints(target).items()
            if k not in ignore and should_include(v)
        }


class NamedTupleSchemaOpts(AnnotationSchemaOpts):
    """
    marshmallow-annotations NamedTuple specific SchemaOpts implementation, provides:

    - converter_factory
    - registry
    - register_as_scheme
    - target
    - field_configs
    - converter
    """

    def _process(self, meta, schema):
        self._extract_from_parents(schema, self._extract_from)
        if self.converter_factory is BaseConverter:
            self.converter_factory = NamedTupleConverter
        self._extract_from(meta)
        self._gather_field_configs(schema, meta)


class NamedTupleSchema(AnnotationSchema):
    """
    Derived class for creating typing.NamedTuple schema with automatic
    post-load conversion to namedtuple instances.
    """

    OPTIONS_CLASS_TYPE = NamedTupleSchemaOpts

    @marshmallow.post_load
    def make_namedtuple(self, data):
        """Post load, deserialize to target namedtuple class."""
        return self.opts.target(**data)

    @marshmallow.post_dump
    def remove_optional(self, data):
        """Post dump, strip default fields from serialized output."""
        return {
            k: v for k, v in data.items() if
            v != self.opts.target._field_defaults.get(k)
        }
