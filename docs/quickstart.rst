.. _quickstart:

##########
Quickstart
##########

This guide will walk you through the basics of using ``marshmallow-annotations``.


*********************
Annotating your class
*********************

Before we can make use of ``marshmallow-annotations`` we first need to annotate
some classes::

    from typing import List

    class Album:
        id: int
        name: str

        def __init__(self, id, name):
            self.id = id
            self.name = name

    class Artist:
        id: int
        name: str
        albums: List[Album]

        def __init__(self, id, name, albums=None):
            self.id = id
            self.name = name
            self.albums = albums if albums is not None else []


.. note::

    If writing this boiler plate is a turn off, consider using
    `attrs <https://www.attrs.org>`_ in conjunction with this library as well::

        import attr

        @attr.s
        class Album:
            id: int = attr.ib()
            name: str = attr.ib()

        @attr.s
        class Artist:
            id: int = attr.ib()
            name: str = attr.ib()
            albums: List[Album] = attr.ib(default=attr.Factory(list))



With these classes defined, we can declare our schema.




***************
Building Schema
***************

The most basic scheme with ``marshmallow-annotations`` is a Meta definition
on an :class:`~marshmallow_annotations.scheme.AnnotationSchema` subclass::

    from marshmallow_annotations import AnnotationSchema

    class AlbumScheme(AnnotationSchema):
        class Meta:
            target = Album
            register_as_scheme = True

    class ArtistScheme(AnnotationSchema):
        class Meta:
            target = Artist
            register_as_scheme = True


Behind the scenes, these short definitions expand into much larger defitions
based on our annotations::

    from marshmallow import fields, Schema

    class AlbumScheme(Schema):
        id = fields.Integer(required=True, allow_none=False)
        name = fields.String(required=True, allow_none=False)


    class ArtistScheme(Schema):
        id = fields.Integer(required=True, allow_none=False)
        name = fields.String(required=True, allow_none=False)
        albums = fields.Nested('AlbumScheme', many=True, required=True, allow_none=False)


If you're curious what the ``register_as_scheme`` option does, this causes the
generated scheme to become associated with the target type in the internal
type mapping and the type will be resolved to its scheme (e.g. in the above
example, future references to ``Album`` in type hints will resolve to
``AlbumScheme``).


With the schema defined we can serialize our ``Artist`` and ``Album`` classes
down to primitives::

    scheme = ArtistScheme()
    scheme.dump(
        Artist(
            id=1, name="Abominable Putridity",
            albums=[
                Album(
                    id=1,
                    name="The Anomalies of Artificial Origin"
                )
            ]
        )
    )

    # {
    #     "albums": [
    #         {
    #             "id": 1,
    #             "name": "The Anomalies of Artificial Origin"
    #         }
    #     ],
    #     "id": 1,
    #     "name": "Abominable Putridity"
    # }


*************
How Types Map
*************


``marshmallow-annotations`` comes preconfigured with a handful of Python
types mapped to marshmallow fields, these fields and their mappings are:

- :class:`bool` maps to :class:`~marshmallow.fields.Boolean`
- :class:`~datetime.date` maps to :class:`~marshmallow.fields.Date`
- :class:`~datetime.datetime` maps to :class:`~marshmallow.fields.DateTime`
- :class:`~decimal.Decimal` maps to :class:`~marshmallow.fields.Decimal`
- :class:`float` maps to :class:`~marshmallow.fields.Float`
- :class:`int` maps to :class:`~marshmallow.fields.Integer`
- :class:`str` maps to :class:`~marshmallow.fields.String`
- :class:`~datetime.time` maps to :class:`~marshmallow.fields.Time`
- :class:`~datetime.timedelta` maps to :class:`~marshmallow.fields.TimeDelta`
- :class:`~uuid.UUID` maps to :class:`~marshmallow.fields.UUID`


List[T]
=======

:class:`typing.List` maps to a special field factory that will attempt
to locate it's type parameter, e.g. ``List[int]`` will map to
``fields.List(fields.Integer())``. Alternatively, ``List[T]`` can generate
a ``fields.Nested(TScheme, many=True)`` if its factory can determine that
its subtype has a scheme factory registered rather than a field factory.


The success of mapping to its type parameter depends on
:ref:`properly configuring your type mappings <customizing>`. If List's
interior typehint can't be resolved, then a
:class:`~marshmallow_annotations.exception.AnnotationConversionError` is raised.


Optional[T]
===========

Another special type is :class:`typing.Optional` (aka :class:`typing.Union[T, None]`).
When ``marshmallow-annotations`` encounters a type hint wrapped in ``Optional``
it generates the base fieldi but will default ``required`` to False and
``allow_none`` to True :ref:`unless overridden <Configuring Fields>`.

.. danger::

    Right now ``marshmallow-annotations`` will only inspect the first member
    of a Union if it thinks it's actually an Optional. The heuristics for this
    are simple and naive: if the type hint is a Union and the last parameter
    is NoneType then it's obviously an ``Optional``.

    The following hint will generate an int even though it's hinting at a type
    that may be either an int, a float or a None::

        Union[int, float, None]


Forward Declaration
===================

``marshmallow-annotations`` can handle forward declarations of a target type
into itself if ``register_as_scheme`` is set to True::

    class MyType:
        children: List[MyType]


    class MyTypeSchema(AnnotationSchema):
        class Meta:
            target = MyType
            register_as_scheme = True


The ``register_as_scheme`` option is very eager and will set the generated
schema class into the register as soon as it determines it can, which occurs
before field generation happens.

.. danger::

    Until Python 3.6.5, evaluation of forward declarations with
    :func:`typing.get_type_hints` -- the method that ``marshmallow-annotations``
    uses to gather hints -- did not work properly. If you are using a class
    that has a forward reference to either itself or a class not yet defined,
    it will fail when used with ``marshmallow-annotations``.

    For these classes, it is recommended to not use forward declarations with
    this library unless you are using 3.6.5+ or backport 3.6.5's fixes to
    ``typing.get_type_hints`` into your application and monkey patch it in.

******************
Configuring Fields
******************

By default, fields will be generated with ``required=True`` and ``allow_none=False``
(however, as mentioned above, an ``Optional`` type hint flips these). However,
sometimes a small adjustment is needed to the generated field. Rather than
require writing out the entire definition, you can use ``Meta.Fields`` to
declare how to build the generated fields.

For example, if ``Artist`` should receive a default name if one is not provided,
it may be configured this way::


    class ArtistScheme(AnnotationSchema):
        class Meta:
            target = Artist
            register_as_scheme = True

            class Fields:
                name = {"default": "One Man Awesome Band"}

Each individual field may be configured here with a dictionary and the values
of the dictionary will be passed to the field's constructor when it is generated.

You may also predefine how fields should be configured on a parent scheme
and the children will inherit those configurations::


    class Track:
        id: Optional[UUID]
        name: str


    class BaseScheme(AnnotationSchema):
        class Meta:
            class Fields:
                id = {"load_only": True}

    class TrackScheme(BaseScheme):
        class Meta:
            target = Track

    TrackScheme().dump({"name": "Wormhole Inversion", "id": str(uuid4())}).data
    # {"name": "Wormhole Inversion"}

Children schema may choose to override the configuration and the scheme will
piece together the correct configuration from the MRO resolution::

    class TrackScheme(BaseScheme):  # as before
        class Meta:
            class Fields:
                id = {"missing": "bdff81f3-dadb-47a7-a0de-fbc892646f47"}

    TrackScheme().dump({"name": "Wormhole Inversion", "id": str(uuid4())}).data
    # {"name": "Wormhole Inversion"}

    TrackScheme().load({"name": "Wormhole Inversion"}).data
    # {
    #   "name": "Wormhole Inversion",
    #   "id": "bdff81f3-dadb-47a7-a0de-fbc892646f47"
    # }


************
Meta Options
************

In addition to the ``Fields`` declaration, ``marshmallow-annotations`` also
provides several other options that can be set in the "Meta" object on a scheme:

- ``target``: The annotated class to generate fields from, if this is not provided
  no fields will be generated however all options related to it will be preserved
  for children schema.

- ``converter_factory``: A callable that accepts a
  :class:`~marshmallow_annotations.base.TypeRegistry` by keyword argument
  ``registry`` and produces a
  :class:`~marshmallow_annotations.base.AbstractConverter` instance. By default
  this is :class:`~marshmallow_annotations.converter.BaseConverter`.

- ``registry``: A registry to use in place of the global type registry, must be
  an instance of :class:`~marshmallow_annotations.base.TypeRegistry`.

- ``register_as_scheme``: If set to true, this will register the generated
  scheme into supplied registry as the type handler for the ``target`` type.
