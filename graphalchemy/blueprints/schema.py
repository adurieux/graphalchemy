#! /usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#                                      IMPORTS
# ==============================================================================


class Model(object):
    pass


class Node(Model):

    def __init__(self, name, metadata, *args, **kwargs):
        self.element_type = name
        self.metadata = metadata
        self.properties = []
        for arg in args:
            self.properties.append(arg)
            arg.model = self

    def register_class(self, class_):
        self.metadata.bind_node(class_, self)

    def is_node(self):
        return True

    def is_relationship(self):
        return False

    def __repr__(self):
        return self.element_type


class Relationship(Model):

    IN = 'in'
    OUT = 'out'
    BOTH = 'both'

    def __init__(self, name, metadata, *args, **kwargs):
        self.label = name
        self.metadata = metadata
        self.properties = []
        for arg in args:
            self.properties.append(arg)
            arg.model = self

    def register_class(self, class_):
        self.metadata.bind_relationship(class_, self)

    def is_node(self):
        return False

    def is_relationship(self):
        return True

    def __repr__(self):
        return self.label


class Adjacency(object):

    def __init__(self, node, relationship, direction=None, multi=None, nullable=None):
        self.node = node
        self.relationship = relationship
        self.direction = direction
        self.multi = multi
        self.nullable = nullable



class ValidationException(Exception):
    pass


class Property(object):

    def __init__(self, name_py, type, **kwargs):
        self.model = None
        self.name_py = name_py
        self.name_db = name_py
        self.type = type
        self.nullable = kwargs.get('nullable', True)
        self.indexed = kwargs.get('indexed', False)

    def to_py(self, value):
        return self.type.to_py(value)

    def to_db(self, value):
        return self.type.to_db(value)

    def validate(self, value):
        if self.nullable == False \
        and value is None:
            return False, [u'Property is not nullable.']
        return self.type.validate(value)

    def __repr__(self):
        return '<'+str(self.model)+'.'+self.name_py+'('+str(self.type)+')>'




class MetaData(object):

    def __init__(self, bind=None, schema=None):
        self._nodes = {}
        self._relationships = {}
        self.schema = schema
        self.bind = bind

    def __repr__(self):
        return 'MetaData(bind=%r)' % self.bind


    def __contains__(self, table_or_key):
        if not isinstance(table_or_key, util.string_types):
            table_or_key = table_or_key.key
        return table_or_key in self.tables

    def for_object(self, obj):
        class_ = obj.__class__
        return self.for_class(class_)

    def for_class(self, class_):
        if class_ in self._nodes:
            return self._nodes[class_]
        if class_ in self._relationships:
            return self._relationships[class_]
        raise Exception('Unmapped class.')

    def for_model(self, model):
        for class_, node_model in self._nodes:
            if model is node_model:
                return class_
        for class_, relationship_model in self._relationships:
            if model is relationship_model:
                return class_
        raise Exception('Unmapped model.')

    def bind_node(self, class_, model):
        if not model.is_node():
            raise Exception('Bound model is not a node !')
        self._nodes[class_] = model
        return self

    def bind_relationship(self, class_, model):
        if not model.is_relationship():
            raise Exception('Bound model is not a relationship !')
        self._relationships[class_] = model
        return self

    def is_node(self, obj):
        return obj.__class__ in self._nodes

    def is_relationship(self, obj):
        return obj.__class__ in self._relationships

    def is_bind(self, obj):
        return self.is_node(obj) or self.is_relationship(obj)



class Validator(object):
    """ Validates each property value of the given object against its specifications.

    Example use :
    >>> ok, errors = self.validator.run(obj)
    True, {}
    """

    def __init__(self, metadata_map, logger=None):
        """ Initializes the validator with a specific metadata map.

        :param metadata_map: The metadata map to validate objects agains.
        :type metadata_map: graphalchemy.blueprints.schema.MetaData
        :param logger: An optionnal logger.
        :type logger: logging.Logger
        """
        self.metadata_map = metadata_map
        self.logger = logger


    def run(self, obj):
        """ Validates an object against its specification.

        :param obj: The object to validate.
        :type obj: graphalchemy.blueprints.schema.Model
        :returns: A boolean stating if the validation was successfull, and the
        eventual list of errors.
        :rtype: boolean, dict<string, list>
        """
        metadata = self.metadata_map.for_object(obj)
        all_errors = {}
        ok = True
        for property in metadata.properties:
            python_value = getattr(obj, property.name_py)
            _ok, errors = property.validate(python_value)
            if _ok:
                self._log('  Property '+str(property)+' is valid')
            else:
                all_errors[property.name_py] = errors
                ok = False
                self._log('  Property '+str(property)+' is invalid : '+" ".join(errors))
        return ok, all_errors


    def _log(self, message, level=10):
        """ Thin wrapper for logging purposes.

        :param message: The message to log.
        :type message: str
        :param level: The level of the log.
        :type level: int
        :returns: This object itself.
        :rtype: graphalchemy.blueprints.schema.Validator
        """
        if self.logger is not None:
            self.logger.log(level, message)
        return self





