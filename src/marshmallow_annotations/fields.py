from marshmallow.fields import Field, missing_

from marshmallow_annotations.base import AbstractConverter, ConfigOptions


class ThunkedField(Field):
    def __init__(
        self,
        converter: AbstractConverter,
        typehint: type,
        opts: ConfigOptions = None,
        *,
        field_name: str = None,
        target: type = None,
    ) -> None:
        # we intentionally do not call the super constructor
        self._converter = converter
        self._typehint = typehint
        self._opts = opts
        self._field_name = field_name
        self._target = target
        self.__inner_field = None
        self._parent = None
        self._name = None

    @property
    def _inner_field(self):
        if self.__inner_field is None:
            self.__inner_field = self._converter.convert(
                self._typehint,
                self._opts,
                field_name=self._field_name,
                target=self._target,
                allow_thunked=False,
            )

            self.__inner_field._add_to_schema(self._parent, self._name)

        return self.__inner_field

    def serialize(self, attr, obj, accessor=None):
        return self._inner_field.serialize(attr, obj, accessor)

    def deserialize(self, value, attr=None, data=None):
        return self._inner_field.deserialize(value, attr, data)

    # proxy these as well just in case someone goes poking around
    def _serialize(self, value, attr, obj):
        return self._inner_field._serialize(self, value, attr, obj)

    def _deserialize(self, value, attr, data):
        return self._inner_field._deserialize(value, attr, data)

    def _inner_field_property(prop_name):
        getter = lambda self: getattr(self._inner_field, prop_name)
        setter = lambda self, value: setattr(self._inner_field, prop_name, value)
        return property(getter, setter)

    default = _inner_field_property("default")
    attribute = _inner_field_property("attribute")
    load_from = _inner_field_property("load_from")
    dump_to = _inner_field_property("dump_to")
    validate = _inner_field_property("validate")
    required = _inner_field_property("required")
    load_only = _inner_field_property("load_only")
    dump_only = _inner_field_property("dump_only")
    missing = _inner_field_property("missing")
    metadata = _inner_field_property("metadata")

    del _inner_field_property

    @property
    def parent(self):
        if self.__inner_field is None:
            return self._parent
        return self._inner_field.parent

    @parent.setter
    def parent(self, value):
        if self.__inner_field is None:
            self._parent = value
        self._inner_field.parent = value

    @property
    def name(self):
        if self.__inner_field is None:
            return self._name
        return self._inner_field.name

    @name.setter
    def name(self, value):
        if self.__inner_field is None:
            self._name = value
        self._inner_field.name = value

    def __repr__(self):
        if self._inner_field is None:
            return f"ThunkedField(UNINITIALIZED)"

        return f"ThunkedField({repr(self._inner_field)})"

    def get_value(self, attr, obj, accessor=None, default=missing_):
        return self._inner_field.get_value(attr, obj, accessor, default)

    def _validate(self, value):
        return self._inner_field._validate(value)

    def fail(self, key, **kwargs):
        return self._inner_field.fail(key, **kwargs)

    def _validate_missing(self, value):
        return self._inner_field._validate_missing(value)
