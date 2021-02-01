from abc import ABC, abstractmethod
from typing import Tuple

from marshmallow.base import FieldABC
from marshmallow.fields import missing_

from marshmallow_annotations.base import AbstractConverter, ConfigOptions, TypeRegistry

__all__ = ("ThunkedField",)


class ProxyingField(FieldABC, ABC):
    """
    A :class:`~marshmallow.field.FieldABC` that proxies into lazily constructed,
    contained field.

    This proxy only promises that all publicly accessible members are
    accessible and makes a best effort to proxy some well known non-public
    members but not all.
    """

    _inner_field: FieldABC

    def __init__(self, *args, **kwargs):
        # intentionally do not call super constructor
        self._inner_field = None
        self._parent = None
        self._name = None

    @abstractmethod
    def _make_inner_field(self) -> FieldABC:
        raise NotImplementedError

    @property
    def inner_field(self):
        if self._inner_field is None:
            self._inner_field = self._make_inner_field()
            self._inner_field._add_to_schema(self.parent, self.name)

        return self._inner_field

    def serialize(self, attr, obj, accessor=None):
        return self.inner_field.serialize(attr, obj, accessor)

    def deserialize(self, value, attr=None, data=None):
        return self.inner_field.deserialize(value, attr, data)

    # proxy these as well just in case someone goes poking around
    def _serialize(self, value, attr, obj):
        return self.inner_field._serialize(self, value, attr, obj)

    def _deserialize(self, value, attr, data):
        return self.inner_field._deserialize(value, attr, data)

    def __getattr__(self, name):
        # without these being excluded, copying the field
        # ends up endlessly recursing when _inner_field is accessed
        if name == "__setstate__" or name == "__getstate__":
            raise AttributeError(name)

        return getattr(self.inner_field, name)

    def __setattr__(self, name, value):
        # since __setattr__ fires for ALL sets of regular fields we have to
        # allow ourselves an escape hatch to set our own fields -- this could
        # be reduced to the known set of fields set in __init__ and everything
        # else is passed down to the inner field :shrug:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            setattr(self.inner_field, name, value)

    @property
    def parent(self):
        if self._inner_field is None:
            return self._parent
        return self.inner_field.parent

    @parent.setter
    def parent(self, value):
        if self._inner_field is None:
            self._parent = value
        self.inner_field.parent = value

    @property
    def name(self):
        if self._inner_field is None:
            return self._name
        return self.inner_field.name

    @name.setter
    def name(self, value):
        if self._inner_field is None:
            self._name = value
        self.inner_field.name = value

    def __repr__(self):
        this_name = self.__class__.__name__
        if self.inner_field is None:
            return f"{this_name}(UNINITIALIZED)"

        return f"{this_name}({repr(self.inner_field)})"

    def get_value(self, attr, obj, accessor=None, default=missing_):
        return self.inner_field.get_value(attr, obj, accessor, default)

    def _validate(self, value):
        return self.inner_field._validate(value)

    def fail(self, key, **kwargs):
        return self.inner_field.fail(key, **kwargs)

    def _validate_missing(self, value):
        return self.inner_field._validate_missing(value)


class ThunkedField(ProxyingField):
    """
    A :class:`~ProxyingField` that delays creating an inner field for a type
    that did not exist in the provided
    :class:`~marshmallow_annotations.base.TypeRegistry` at the time that it
    was requested.

    The type must exist in the provided
    :class:`~marshmallow_annotations.base.TypeRegistry` by the time the inner
    field is accessed, otherwise a
    :class:`~marshmallow_annotations.exceptions.AnnotationConversionError`
    may be thrown when it is accessed.
    """

    def __init__(
        self,
        registry: TypeRegistry,
        target: type,
        converter: AbstractConverter,
        subtypes: Tuple[type],
        kwargs: ConfigOptions,
    ) -> None:
        super().__init__()
        self._registry = registry
        self._target = target
        self._converter = converter
        self._subtypes = subtypes
        self._kwargs = kwargs

    def _make_inner_field(self):
        field_constructor = self._registry.get(self._target)
        return field_constructor(self._converter, self._subtypes, self._kwargs)
