def create_attribute_descriptor(value_type: object):
    """attribute descriptor constructor function that lets you create a
    dynamic descriptor class to be used by any attribute field we want

    :param value_type: object
    """

    class AttributeDescriptor:
        """AttributeDescriptor class defines our own custom descriptor, a
        descriptor in python lets use the before set and get hooks of any
        python variable to add any logic we want to be executed before this
        hooks
        """

        def __set_name__(self, owner, name):
            """Set the public and private names for the attribute"""
            self.public_name = name
            self.private_name = f"_{name}"

        def __get__(self, obj, objtype=None):
            """returns the attribute we need"""
            value = getattr(obj, self.private_name)
            return value

        def __set__(self, obj, value):
            """Executes our custom logic before we set the value to the
            attribute. This let's us create a generic structure to be used with
            any attribute at the same time as we add a type control to prevent
            the assignment of invalid data"""
            if isinstance(value, value_type):
                setattr(obj, self.private_name, value)
            else:
                raise TypeError(f"{self.name!r} values must be of type {self.type!r}")

    return AttributeDescriptor
