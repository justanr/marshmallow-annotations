"""Specialized components for Python 3.6 NamedTuple annotations."""

import marshmallow

from marshmallow_annotations.scheme import (
    AnnotationSchema,
    AnnotationSchemaOpts,
    BaseConverter,
)


__all__ = ("NamedTupleConverter", "NamedTupleSchemaOpts", "NamedTupleSchema")


class NamedTupleConverter(BaseConverter):
    def _get_field_defaults(self, item):
        return getattr(item, "_field_defaults", {})


class NamedTupleSchemaOpts(AnnotationSchemaOpts):
    """
    NamedTuple specific AnnotationSchemaOpts, additionally provides:

    - dump_default_fields
    """

    def __init__(self, meta, *args, **kwargs):
        super().__init__(meta, *args, **kwargs)
        self.dump_default_fields = getattr(meta, "dump_default_fields", True)


class NamedTupleSchema(AnnotationSchema):
    """
    Derived class for creating typing.NamedTuple schema with automatic
    post-load conversion to namedtuple instances.
    """

    OPTIONS_CLASS_TYPE = NamedTupleSchemaOpts

    class Meta:
        converter_factory = NamedTupleConverter

    @marshmallow.post_load
    def make_namedtuple(self, data):
        """Post load, deserialize to target namedtuple class."""
        return self.opts.target(**data)

    @marshmallow.post_dump
    def remove_optional(self, data):
        """Post dump, strip default fields from serialized output."""
        if self.opts.dump_default_fields:
            return data
        else:
            default_values = self.opts.converter._get_field_defaults(self.opts.target)
            return {k: v for k, v in data.items() if v != default_values.get(k)}
