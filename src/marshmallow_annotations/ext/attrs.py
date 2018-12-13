from typing import AbstractSet, Iterable

from attr import NOTHING, Attribute, Factory

from marshmallow import missing, post_load

from ..base import GeneratedFields, NamedConfigs
from ..exceptions import AnnotationConversionError
from ..scheme import AnnotationSchema, BaseConverter

__all__ = ("AttrsConverter", "AttrsSchema")

__SENTINEL = object()


def _is_attrs(target):
    return getattr(target, "__attrs_attrs__", __SENTINEL) is not __SENTINEL


def _get_attr_from_attrs(attrs: Iterable[Attribute], name: str) -> Attribute:
    attrs = [a for a in attrs if a.name == name]
    return attrs[0]


def _should_include_default(attr):
    if not attr.init:
        return False

    # an attrs factory cannot be copied over to a marshmallow field despite
    # marshmallow fields being able to accept a callable there because some
    # attrs factories accept the newly created instance as an argument
    # which is something marshmallow doesn't support

    # see following issue for mypy ignore
    # https://github.com/python/mypy/issues/3060
    return attr.default != NOTHING and not isinstance(  # type: ignore
        attr.default, Factory
    )


class AttrsConverter(BaseConverter):
    def convert_all(
        self,
        target: type,
        ignore: AbstractSet[str] = frozenset([]),  # noqa
        configs: NamedConfigs = None,
    ) -> GeneratedFields:
        self._ensure_all_hints_are_attribs(target, ignore)
        return super().convert_all(target, ignore, configs)

    def _get_field_defaults(self, target):
        return {
            a.name: a.default
            for a in target.__attrs_attrs__
            if _should_include_default(a)
        }

    def _preprocess_typehint(self, typehint, kwargs, field_name, target):
        # while this seems contradictory to this converter, we need to
        # ignore attrs specific actions when a container type, e.g. a List[T],
        # contains a non-attrs manufactured type because this is recursively
        # called during schema generation.
        # however those types will still require an entry in the registry
        # is handled outside this converter
        if not _is_attrs(target):
            return

        attr = _get_attr_from_attrs(target.__attrs_attrs__, field_name)

        if attr.default != NOTHING:
            # default to optional even if the typehint isn't
            # but don't override the user saying otherwise
            kwargs.setdefault("required", False)
            kwargs.setdefault("missing", missing)

    def _postprocess_typehint(self, typehint, kwargs, field_name, target):
        # see _preprocess_typehint for details
        if not _is_attrs(target):
            return

        attr = _get_attr_from_attrs(target.__attrs_attrs__, field_name)

        if not attr.init:
            # force into dump only mode if the field won't be accepted
            # into __init__ -- even if the user told us otherwise
            kwargs["dump_only"] = True

        if attr.metadata:
            kwargs.update(attr.metadata)

    def _ensure_all_hints_are_attribs(self, target, ignore):
        # This would happen if an attrs handled class was subclassed by
        # a plain ol' python class and added more non-ignored type hinted
        # fields. In theory we could handle this but we won't
        hints = {k for k, _ in self._get_type_hints(target, ignore)}
        attribs = {a.name for a in target.__attrs_attrs__ if a.name not in ignore}

        if hints != attribs:
            raise AnnotationConversionError(
                f"Mismatched hints and attr.ibs. Got hints: {hints} "
                f"but attr.ibs {attribs}"
            )


class AttrsSchema(AnnotationSchema):
    """
    Schema for handling ``attrs`` based targets, adds automatic load conversion
    into the target class and specifies the
    :class:`~marshmallow_annotations.ext.attrs.AttrsConverter` as the converter
    factory.
    """

    class Meta:
        converter_factory = AttrsConverter

    @post_load
    def make_object(self, data):
        return self.opts.target(**data)
