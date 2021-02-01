.. _usage

#####
Usage
#####

This guide will walk through everything needed to creating schemas, registering
new fields and all the options availabe for schema registration.

*******************
Generating a scheme
*******************

Generating schemas from classes with type annotations is the bread and butter
of this library. Given the following classes::

    from typing import List

    class Album:
        id: int
        name: str

    class Artist:
        id: int
        name: str
        albums: List[Album]


Schemes can be generated for them with the following::

    from marshmallow_annotations import AnnotationSchema

    class AlbumSchema(AnnotationSchema):
        class Meta:
            target = Album
            register_as_scheme = True

    class ArtistSchema(AnnotationSchema):
        class Meta:
            target = Artist
            register_as_scheme = True


This example would both generate the schema for each type and allow the generated
schemas to be used by other generated schemas. Registration is not automatic
and is facililated by the ``register_as_scheme`` field.


There are other options available for the meta options on AnnotationSchema. These
are all in addition to the usual meta options provided by marshmallow

* ``target``: The class to generate a schema from
* ``register_as_scheme``: Registers the scheme into the type registry
* ``registry``: By default the global type registry is used, but this can be
  provided to use a separate type registry
* ``converter_factory``: By default the


*************************
Adding new field mappings
*************************

Registering new fields is operated by instances of
:class:`~marshmallow_annotations.base.TypeRegistry` using either the
``register_field_for_type`` or ``register_scheme_constructor`` method::


    from marshmallow_annotations import registry
    from ipaddress import IPv4Address
    from .fields import IPAddressField

    registry.register_field_for_type(IPv4Address, IPAddressField)


And now ``marshmallow_annotations`` can recognize ``IPv4Address`` type hints
as generating ``IPAddressField`` instances.

.. note::

    This example uses the default, global registry. If you are using a custom
    :class:`~marshmallow_annotations.base.TypeRegistry` or a separate instance
    of :class:`~marshmallow_annotations.registry.DefaultTypeRegistry` you will
    need to register the type hint into that registry as well or instead.

.. danger::

    :class:`~marshmallow_annotations.registry.DefaultTypeRegistry` does not
    check for preexisting entries before adding a new field mapping. This means
    that is is possible to overwrite an existing field mapping (which will not
    affect already generated schemas unless a
    :class:`~marshmallow_annotations.fields.ThunkedField` was generated).

    In some circumstances this may be beneficial behavior, however it could
    lead to hard to track down bugs and issues.


For more complicated types, an entire scheme may be registered into the registry
manually. This is useful if a scheme was created manually and not generated::

    from marshmallow_annotations.registry import registry
    from myapp.entites import Game
    from myapp.schema import GameScheme

    registry.register_scheme_constructor(Game, GameScheme)
    # alternatively, the scheme name may be used to register:
    registry.register_scheme_constructor(Game, "GameScheme")


.. note::

    When using the name registration, any string form supported by
    :class:`~marshmallow.fields.Nested` is acceptable. Meaning both
    ``"GameScheme"`` and ``myapp.schema.GameScheme`` should both work
    as long as the scheme has entered into marshmallow scheme registry.


If even more control over registration of field is necessary, all the mechanics
are also exposed for use. Both ``field_factory`` and ``scheme_factory`` are
helper methods that create a ``FieldFactory``. If a custom ``FieldFactory``
is needed, all that is required is a callable that accepts:

1. An instance of :class:`~marshmallow_annotations.base.AbstractConverter`
2. A tuple of subtypes, which may or may not be empty when called
3. A :class:`~marshmallow_annotations.base.ConfigOptions` which is essentially
   a type hint for a ``**kwargs`` dictionary to be passed to the field to be constructed

And then returns an instance of :class:`marshmallow.base.FieldABC`

For example, the registration for :class:`typing.List` uses a custom factory
that looks like::

    def _list_converter(converter, subtypes, opts):
        if converter.is_scheme(subtypes[0]):
            opts["many"] = True
            return converter.convert(subtypes[0], opts)

        sub_opts = opts.pop("_interior", {})
        return fields.List(converter.convert(subtypes[0], sub_opts), **opts)


