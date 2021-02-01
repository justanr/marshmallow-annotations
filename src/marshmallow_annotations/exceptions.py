from marshmallow.exceptions import MarshmallowError

__all__ = ("AnnotationConversionError", "MarshmallowAnnotationError")


class MarshmallowAnnotationError(MarshmallowError):
    pass


class AnnotationConversionError(MarshmallowAnnotationError):
    pass
