from marshmallow.schema import Schema, SchemaMeta

from .converter import BaseConverter
from .registry import TypeRegistry


class AnnotationSchemaMeta(SchemaMeta):

    @staticmethod
    def __new__(mcls, name, bases, attrs, **k):
        cls = super().__new__(mcls, name, bases, attrs)
        meta = getattr(cls, "Meta", None)
        cls._register_as_scheme_for_target(meta)
        return cls

    @classmethod
    def get_declared_fields(mcls, klass, cls_fields, inherited_fields, dict_cls):
        fields = super().get_declared_fields(
            klass, cls_fields, inherited_fields, dict_cls
        )

        meta = getattr(klass, "Meta", None)

        if not meta:
            return fields

        target = getattr(meta, "target", None)

        if target is None:
            return fields

        converter_factory = getattr(meta, "converter", BaseConverter)

        # weeeee circular references!
        meta.converter = converter = converter_factory(klass)

        # ignore anything explicitly declared on this scheme
        # or any parent scheme
        ignore = fields.keys()
        fields.update(converter.convert_all(target, ignore))

        return fields

    @classmethod
    def _register_as_scheme_for_target(cls, meta):
        if meta is None:
            return

        should_register = getattr(meta, "register_as_scheme", False)
        target = getattr(meta, "target", None)

        if should_register and target:
            meta.converter.registry.register_scheme_constructor(target, cls)


class AnnotationSchema(Schema, metaclass=AnnotationSchemaMeta):
    pass
