.. _customizing:

###########
Customizing
###########


There are several ways to customize how fields are generated from types in your
application.

********************
Custom Field Mapping
********************

The most straight forward is registering custom field mappings into the global
registry::

   from marshmallow_annotations import registry
   from ipaddress import IPv4Address
   from some_extension IPAddressField


   registry.register_field_for_type(IPv4Address, IPAddressField)


And now ``marshmallow_annotations`` will recognize ``IPv4Address`` hints as
generating an ``IPAddressField``.


.. danger::

    Registrations don't check for preexisting entries before being added, and
    it's entirely possible to overwrite an existing registration. In some
    circumstances this may be useful however it may lead to hard to track
    down bugs.


For more complicated types, an entire scheme may be registered into the registry
as well::

    from myapp.entities import Game
    from myapp.schema import GameScheme

    registry.register_scheme_constructor(Game, GameScheme)
    # alternatively:
    registry.register_scheme_constructor(Game, 'GameScheme')


If more customized behavior is needed, ``field_factory`` and ``register``
are also exposed. ``field_factory`` is the decorator form of ``register``
so it will not be covered here. ``register`` accepts two arguments:

1. The type to associate with
2. A callable that accepts:

   - A :class:`~marshmallow_annotations.base.AbstractConverter` instance
   - A tuple of type hints
   - A dictionary of configuration values to pass to the generated field


For example, :class:`typing.List` has a custom factory that resembles::

    def _list_converter(converter, subtypes, opts):
        return fields.List(converter.convert(subtypes[0]), **opts)


Under the hood, ``register_scheme_constructor`` and ``register_field_for_type``
use generalized versions of such a converter, these are exposed as
:meth:`~marshmallow_annotations.registry.default_scheme_constructor` and
:meth:`~marshmallow_annotations.registry.default_field_factory` and are
availbe for use if needed.

***************************
Using a non-Global registry
***************************

Since mutable, global state doesn't sit well with everyone it is also possible
to use a non-global registry by creating your own instance of
:class:`marshmallow_annotations.registry.TypeRegistry`::

    from marshmallow_annotations import DefaultTypeRegistry

    my_registry = DefaultTypeRegistry()

It's also possible to pass a dictionary that maps a type to a field factory
into the initializer and pre-configure your registry instance with those
types::

    conf = {IPv4Address: default_field_factory(IPAddressField)}

    my_registry = DefaultTypeRegistry(conf)


***************
Custom Registry
***************

If :class:`~marshmallow_annotations.registry.DefaultTypeRegistry` isn't meeting
your needs, :class:`~marshmallow_annotations.base.TypeRegistry` is available
for implementation as well.


*****************
Custom Converters
*****************

Another customization point is implementing your own
:class:`~marshmallow_annotations.base.AbstractConverter` class as well to
provide to schema definitions.
