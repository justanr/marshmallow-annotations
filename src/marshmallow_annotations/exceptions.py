from marshmallow.exceptions import MarshmallowError


class MarshmallowAnnotationError(MarshmallowError):
    pass


class AnnotationConversionError(MarshmallowAnnotationError):
    pass
