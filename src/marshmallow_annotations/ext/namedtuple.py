"""Specialized components for Python 3.6 NamedTuple annotations."""

import marshmallow

from marshmallow_annotations.scheme import AnnotationSchema


class NamedTupleSchema(AnnotationSchema):
    """
    Derived class for creating typing.NamedTuple schema with automatic
    post-load conversion to namedtuple instances.
    """

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
