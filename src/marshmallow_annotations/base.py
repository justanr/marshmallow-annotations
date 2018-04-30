from abc import ABC, abstractmethod
from typing import AbstractSet, Any, Callable, Dict, Optional, Tuple, Union

from marshmallow.base import FieldABC, SchemaABC

from .exceptions import MarshmallowAnnotationError

ConfigOptions = Optional[Dict[str, Any]]
NamedConfigs = Optional[Dict[str, ConfigOptions]]
GeneratedFields = Dict[str, FieldABC]


class AbstractConverter(ABC):

    @abstractmethod
    def convert(self, typehint: type, opts: ConfigOptions = None) -> FieldABC:
        pass

    @abstractmethod
    def convert_all(
        self,
        target: type,
        ignore: AbstractSet[str] = frozenset([]),
        configs: NamedConfigs = None,
    ) -> GeneratedFields:
        pass


FieldConstructor = Callable[[AbstractConverter, Tuple[type], Dict[str, Any]], FieldABC]


class TypeRegistry(ABC):

    @abstractmethod
    def register(self, target: type, constructor: FieldConstructor) -> None:
        pass

    @abstractmethod
    def field_constructor(
        self, target: type
    ) -> Callable[[FieldConstructor], FieldConstructor]:
        pass

    @abstractmethod
    def get(self, target: type) -> FieldConstructor:
        pass

    @abstractmethod
    def register_field_for_type(self, target: type, field: FieldABC) -> None:
        pass

    @abstractmethod
    def register_scheme_constructor(
        self, target: type, scheme_or_name: Union[str, SchemaABC]
    ):
        pass

    # ideally this is never used and custom implementations provide their
    # contains implementation as well
    def __contains__(self, target: type) -> bool:  # pragma: no cover
        try:
            return bool(self.get(target))
        except MarshmallowAnnotationError:
            return False
