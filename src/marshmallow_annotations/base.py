from abc import ABC, abstractmethod
from typing import AbstractSet, Any, Callable, Dict, Optional, Tuple, Union

from marshmallow.base import FieldABC, SchemaABC

ConfigOptions = Optional[Dict[str, Any]]
NamedConfigs = Optional[Dict[str, ConfigOptions]]
GeneratedFields = Dict[str, FieldABC]


class AbstractConverter(ABC):
    """
    Converters handle gathering type hints and consulting with a
    :class:`~marshmallow_annotations.base.TypeRegistry` in order to produce
    marshmallow field instances::


        from marshmallow_annotations import BaseConverter

        converter = BaseConverter(registry)
        converter.convert(int, {"required": False})
        # marshmallow.fields.Integer(...)


    This abstract class is provided primarily for type hinting purposes
    but also allows implementations outside of the default implementation in
    this library.
    """

    @abstractmethod
    def convert(
        self,
        typehint: type,
        opts: ConfigOptions = None,
        *,
        field_name: str = None,
        target: type = None
    ) -> FieldABC:
        """
        Used to convert a type hint into a :class:`~marshmallow.base.FieldABC`
        instance.

        :versionchanged: 2.2.0 Added field_name and target optional keyword
            only arguments
        """
        pass

    @abstractmethod
    def convert_all(
        self,
        target: type,
        ignore: AbstractSet[str] = frozenset([]),  # noqa: B008
        configs: NamedConfigs = None,
    ) -> GeneratedFields:
        """
        Used to transform a type with annotations into a dictionary mapping
        the type's attribute names to :class:`~marshmallow.base.FieldABC`
        instances.
        """
        pass

    @abstractmethod
    def is_scheme(self, typehint: type) -> bool:
        """
        Used to check if the typehint passed if associated to a scheme or
        a regular field constructor.
        """
        pass


FieldFactory = Callable[[AbstractConverter, Tuple[type], Dict[str, Any]], FieldABC]


class TypeRegistry(ABC):
    """
    Abstraction representation of a registry mapping Python types to marshmallow
    field types.

    This abstract class is provided primarily for type hinting purposes but also
    allows implementations outside of the default implementation in this library.
    """

    @abstractmethod
    def register(self, target: type, constructor: FieldFactory) -> None:
        """
        Registers a raw field factory for the specified type::

            from marshmallow import fields

            def custom(converter, subtypes, opts):
                return fields.Raw(**opts)

            registry.register(bytes, custom)


        """
        pass

    def field_factory(self, target: type) -> Callable[[FieldFactory], FieldFactory]:
        """
        Decorator form of register::

            @register.field_factor(bytes)
            def custom(converter, subtypes, opts):
                return fields.Raw(**opts)

        Returns the original function so it can be used again if needed.
        """

        def field_factory(constructor: FieldFactory) -> FieldFactory:
            self.register(target, constructor)
            return constructor

        return field_factory

    @abstractmethod
    def get(self, target: type) -> FieldFactory:
        """
        Retrieves a field factory from the registry. If it doesn't exist,
        this may raise a
        :class:`~marshmallow_annotations.exception.AnnotationConversionError`::

            registry.get(str)  # string field factory
            registry.get(object)  # raises AnnotationConversionError

        """
        pass

    @abstractmethod
    def register_field_for_type(self, target: type, field: FieldABC) -> None:
        """
        Registers a raw marshmallow field to be associated with a type::

            from typing import NewType
            Email = NewType("Email", str)

            registry.register_field_for_type(Email, EmailField)

        """
        pass

    @abstractmethod
    def register_scheme_factory(
        self, target: type, scheme_or_name: Union[str, SchemaABC]
    ) -> None:
        """
        Registers an existing scheme or scheme name to be associated with a type::

            from myapp.schema import ArtistScheme
            from myapp.entities import Artist

            registry.register_scheme_factory(Artist, ArtistScheme)

        """
        pass

    @abstractmethod
    def has(self, target: type) -> bool:
        """
        Allows safely checking if a type has a companion field mapped already::

            registry.has(int)     # True
            registry.has(object)  # False

        May also be used with in::

            int in registry     # True
            object in registry  # False
        """
        pass

    def __contains__(self, target: type) -> bool:  # pragma: no cover
        return self.has(target)
