.. _attrsintegration:

#####
attrs
#####

If you are using `attrs <http://attrs.org>`_, you can use the extension
:class:`~marshmallow_annotations.ext.attrs.AttrsSchema` to generate your schema.


************
Installation
************

This extension ships with ``marshmallow-annotations`` beginning in v2.2.0 and
is available for import normally. You may specify
``marshmallow-annotations[attrs]`` as the install target to automatically
install attrs along side marshmallow-annotations.


*********************
Attrs Integration API
*********************

This extension modifies loading behavior to deserialize directly into instances
of the target class. To handle automatic generation, you must specify your
attr class to have the ``auto_attribs`` option to generate matching ``attr.ib``
instances from purely typehinted fields::


    from datetime import timedelta
    import attr
    from marshmallow_annotations.ext.attrs import AttrsSchema


    @attr.s(auto_attribs=True)
    class Track:
        name: str  # no attr.ib -- attrs will generate one with auto_attribs
        length: timedelta = attr.ib(factory=timedelta)

    class TrackSchema(AttrsSchema):
        class Meta:
            target = Track

    serializer = TrackSchema()
    loaded = serializer.load({"name": "Letting Them Fall"}).data
    # Track(name="Letting Them Fall", length=timedelta(0))
    serializer.dump(loaded).data
    # {"name": "Letting Them Fall", "length": 0}


The attrs integration makes a few changes to the normal assumptions the normal
schema generation makes:

- If an ``attr.ib`` has a default value (not a factory), it is put on the
  generated field as the missing value and the field is marked optional (though
  not ``allow_none``).
- If an ``attr.ib`` has a default factory, the field is marked optional but
  the factory is not moved to the generated field (this is despite that
  marshmallow fields can accept callables as ``missing``, some factories accept
  the new instance as an argument and marshmallow cannot handle this).
- If an ``attr.ib`` is passed ``init=False`` then the generated field is marked
  ``dump_only=True`` even if the ``Meta.Fields`` setting set it to
  ``dump_only=False`` since the instance constructor cannot accept this value.

It is possible to override the ``missing`` value and ``required=False`` by
changing these in the ``Meta.Fields``.


.. warning::

    If you use attrs to generate a class and then create a subclass not handled
    by attrs, this extension with throw an
    :class:`~marshmallow_annotations.exceptions.AnnotationConversionError`
    if additional non-class level fields are added::

        @attr.s(auto_attribs=True)
        class SomeClass:
            x: int
            y: int

        class SomeSubClass(SomeClass):
            z: int

    Attempting to generate an
    :class:`~marshmallow_annotations.ext.attrs.AttrsSchema` from ``SomeSubClass``
    will fail as there is no matching ``attr.ib`` for ``z``.

****************
Provided Classes
****************
.. autoclass:: marshmallow_annotations.ext.attrs.AttrsConverter
.. autoclass:: marshmallow_annotations.ext.attrs.AttrsSchema
