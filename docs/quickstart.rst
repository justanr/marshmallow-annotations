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

    import typing as t

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

******
Schema
******

The most basic scheme with ``marshmallow-annotations`` is a Meta definition
on the an :class:`~marshmallow.scheme.AnnotationSchema` subclass::

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
        albums = fields.List(fields.Nested('AlbumScheme'), required=True, allow_none=False)


.. note::

    Right now ``marshmallow-annotations`` generates ``List(Nested(SchemeName))``
    rather than ``Nested(SchemaName, many=True)``

If you're curious what the ``register_as_scheme`` option does, this causes the
generated scheme to become associated with the target type in the internal
type mapping.


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



******************
Configuring Fields
******************
