from typing import List

import marshmallow as ma
import pytest
from marshmallow_annotations import AnnotationSchema
from marshmallow_annotations.exceptions import AnnotationConversionError

try:
    from marshmallow_annotations.ext.attrs import AttrsSchema
    import attr
except ImportError:
    pytestmarker = pytest.skip("attrs not installed")


def int_factory() -> int:
    return 1


@attr.s(auto_attribs=True)
class SomeClass:
    a: int = attr.ib()
    # non-required, missing is marshmallow.missing
    # also, it's okay mypy, we got this
    b: int = attr.ib(factory=int_factory)  # type: ignore
    # dump only field
    c: int = attr.ib(default=1, init=False)
    # non-required, missing is 1
    d: int = attr.ib(default=1)
    # Include metadata
    e: str = attr.ib(default="", metadata={"hi": "world"})
    # container of non-attrs class
    f: List[int] = attr.ib(factory=list)


@attr.s(auto_attribs=True)
class SomeOtherClass:
    a: int = attr.ib()
    b: "List[SomeOtherClass]" = attr.ib()


@attr.s(auto_attribs=True)
class ContainerClass:
    a: List[SomeClass] = attr.ib(factory=list)


class NotAnAttrsClass:
    a: int

    def __init__(self, a: int) -> None:
        self.a = a


@attr.s(auto_attribs=True)
class ContainsNotAttrs:
    a: NotAnAttrsClass = attr.ib()


def test_properly_converts_attrs_class_to_schema(registry_):
    class SomeClassSchema(AttrsSchema):
        class Meta:
            registry = registry_
            target = SomeClass

    s = SomeClassSchema()

    result = s.load({"a": 1})

    # mypy thinks we're missing arguments for some reason
    expected = SomeClass(a=1)  # type: ignore
    assert not result.errors
    assert result.data == expected


def test_dumps_all_attributes(registry_):
    class SomeClassSchema(AttrsSchema):
        class Meta:
            registry = registry_
            target = SomeClass

    s = SomeClassSchema()
    result = s.dump(SomeClass(a=99))  # type: ignore

    expected = {"a": 99, "b": 1, "c": 1, "d": 1, "e": "", "f": []}
    assert not result.errors
    assert result.data == expected


def test_cant_convert_non_attrs_subclass(registry_):
    class SomeSubclass(SomeClass):
        x: int

    with pytest.raises(AnnotationConversionError) as excinfo:

        class SomeSubclassSchema(AttrsSchema):
            class Meta:
                registry = registry_
                target = SomeSubclass

    assert "x" in str(excinfo.value)


def test_can_convert_forward_references_to_self(registry_):
    class SomeOtherClassSchema(AttrsSchema):
        class Meta:
            registry = registry_
            target = SomeOtherClass
            register_as_scheme = True

    inst = SomeOtherClass(a=1, b=[SomeOtherClass(a=2, b=[])])
    expected = {"a": 1, "b": [{"a": 2, "b": []}]}
    result = SomeOtherClassSchema().dump(inst)

    assert not result.errors
    assert result.data == expected


def test_metadata_included(registry_):
    class SomeClassSchema(AttrsSchema):
        class Meta:
            registry = registry_
            target = SomeClass

    s = SomeClassSchema()
    assert s.fields["e"].metadata.keys() == {"hi"}
    assert s.fields["e"].metadata["hi"] == "world"


def test_handles_contained_attrs_class_properly(registry_):
    class SomeClassSchema(AttrsSchema):
        class Meta:
            registry = registry_
            target = SomeClass
            register_as_scheme = True

    class ContainerClassSchema(AttrsSchema):
        class Meta:
            registry = registry_
            target = ContainerClass

    inst = ContainerClass(a=[SomeClass(a=99, b=1, d=1, f=[])])
    s = ContainerClassSchema()
    expected = {"a": [{"a": 99, "b": 1, "c": 1, "d": 1, "e": "", "f": []}]}
    result = s.dump(inst)
    assert not result.errors
    assert result.data == expected


def test_handles_contained_not_attrs_class(registry_):
    class NotAnAttrsClassSchema(AnnotationSchema):
        class Meta:
            registry = registry_
            target = NotAnAttrsClass
            register_as_scheme = True

    class ContainsNotAttrsSchema(AttrsSchema):
        class Meta:
            registry = registry_
            target = ContainsNotAttrs

    inst = ContainsNotAttrs(a=NotAnAttrsClass(1))
    s = ContainsNotAttrsSchema()
    expected = {"a": {"a": 1}}
    result = s.dump(inst)
    assert not result.errors
    assert result.data == expected
