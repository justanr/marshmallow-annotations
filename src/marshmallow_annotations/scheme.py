from inspect import getmro

from marshmallow.schema import Schema, SchemaMeta, SchemaOpts

from .converter import BaseConverter
from .registry import registry
from typing import Dict, Any


class AnnotationSchemaOpts(SchemaOpts):
    """
    marshmallow-annotations specific SchemaOpts implementation, provides:

    - converter_factory
    - registry
    - register_as_scheme
    - target
    - field_configs
    - converter
    """

    def __init__(self, meta, schema=None):
        super().__init__(meta)
        self.__sentinel = object()
        self.field_configs: Dict[str, Dict[str, Any]] = {}

        self._process(meta, schema)
        self._finalize()
        self.converter = self.converter_factory(registry=self.registry)

        if schema is not None and self.register_as_scheme and hasattr(self, "target"):
            self.converter.registry.register_scheme_factory(self.target, schema)

        del self.__sentinel

    def _process(self, meta, schema):
        self._extract_from_parents(schema, self._extract_from)
        self._extract_from(meta)
        self._gather_field_configs(schema, meta)

    def _extract_from_parents(self, schema, f):
        # can't look at just next parent
        # they may or may be an AnnotationSchema
        # so we need to walk backwards from object to get the correct
        # combination of settings
        for parent in reversed(getmro(schema)):
            opts = getattr(parent, "opts", self.__sentinel)
            if opts is self.__sentinel:
                continue

            f(opts)

    def _extract_from(self, source):
        if hasattr(source, "converter_factory"):
            self.converter_factory = source.converter_factory
        if hasattr(source, "register_as_scheme"):
            self.register_as_scheme = source.register_as_scheme
        if hasattr(source, "target"):
            self.target = source.target
        if hasattr(source, "registry"):
            self.registry = source.registry

    def _gather_field_configs(self, schema, meta):
        def merge_field_configs(opts):
            field_configs = getattr(opts, "field_configs", self.__sentinel)

            if field_configs is self.__sentinel:
                return

            for k, v in field_configs.items():
                config = self.field_configs.setdefault(k, {})
                config.update(dict(v))

        self._extract_from_parents(schema, merge_field_configs)

        defaults = getattr(meta, "Fields", self.__sentinel)
        if defaults is self.__sentinel:
            return

        for k, v in defaults.__dict__.items():
            if k.startswith("_"):
                continue

            self.field_configs.setdefault(k, {}).update(v)

    def _finalize(self):
        self.converter_factory = getattr(self, "converter_factory", BaseConverter)
        self.register_as_scheme = getattr(self, "register_as_scheme", False)
        self.registry = getattr(self, "registry", registry)


class AnnotationSchemaMeta(SchemaMeta):
    @classmethod
    def get_declared_fields(mcls, klass, cls_fields, inherited_fields, dict_cls):
        fields = super().get_declared_fields(
            klass, cls_fields, inherited_fields, dict_cls
        )

        target = getattr(klass.opts, "target", None)

        if target is None:
            return fields

        converter = klass.opts.converter

        # ignore anything explicitly declared on this scheme
        # or any parent scheme, also ignore anything explicitly
        # passed into exclude
        ignore = set(fields) | set(klass.opts.exclude)
        fields.update(converter.convert_all(target, ignore, klass.opts.field_configs))

        return fields


class AnnotationSchema(Schema, metaclass=AnnotationSchemaMeta):
    """
    Base class for creating annotation schema with::

        from marshmallow_annotations import AnnotationSchema
        from my.app.entities import Artist

        class ArtistScheme(AnnotationSchema):
            class Meta:
                target = Artist
                register_as_scheme = True

    """

    OPTIONS_CLASS_TYPE = AnnotationSchemaOpts

    @classmethod
    def OPTIONS_CLASS(cls, meta):
        return cls.OPTIONS_CLASS_TYPE(meta, cls)
