from typing import AbstractSet, Iterable

from attr import NOTHING, Attribute, Factory

from marshmallow import missing, post_load

from ..base import GeneratedFields, NamedConfigs
from ..exceptions import AnnotationConversionError
from ..scheme import AnnotationSchema, BaseConverter

__all__ = ("AttrsConverter", "AttrsSchema")


def _get_attr_from_attrs(attrs: Iterable[Attribute], name: str) -> Attribute:
    attrs = [a for a in attrs if a.name == name]
    return attrs[0]


def _should_include_default(attr):
    if not attr.init:
        return False

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

    def _preprocess_typehint(self, typehing, kwargs, field_name, target):
        attr = _get_attr_from_attrs(target.__attrs_attrs__, field_name)

        if attr.default != NOTHING:
            # default to optional even if the typehint isn't
            # but don't override the user saying otherwise
            kwargs.setdefault("required", False)
            kwargs.setdefault("missing", missing)

    def _postprocess_typehint(self, typehint, kwargs, field_name, target):
        attr = _get_attr_from_attrs(target.__attrs_attrs__, field_name)

        if not attr.init:
            # force into dump only mode if the field won't be accepted
            # into __init__ -- even if the user told us otherwise
            kwargs["dump_only"] = True

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
