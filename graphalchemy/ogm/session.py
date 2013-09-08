
from graphalchemy.ogm.identity import IdentityMap
from graphalchemy.ogm.unitofwork import UnitOfWork

class Session(object):

    def __init__(self, client, metadata, logger=None):
        self.identity_map = IdentityMap()
        self.metadata_map = metadata
        self.client = client
        self.logger = logger

        self._update = []
        self._delete = []
        self._new = []


    def add(self, instance):
        if instance in self.identity_map:
            self._update.append(instance)
        else:
            self._new.append(instance)
        return self


    def flush(self):

        uow = UnitOfWork(self.client, self.identity_map, self.metadata_map, logger=self.logger)

        # We need to save nodes first
        for obj in self._new:
            if self.metadata_map.is_node(obj):
                uow.register_object(obj, 'new')
                self._log("Inserted "+str(obj))
        for obj in self._new:
            if self.metadata_map.is_relationship(obj):
                uow.register_object(obj, 'new')
                self._log("Inserted "+str(obj))

        # Update all other nodes
        for obj in self._update:
            if self.metadata_map.is_node(obj):
                uow.register_object(obj, 'update')
                self._log("Updated "+str(obj))
        for obj in self._update:
            if self.metadata_map.is_relationship(obj):
                uow.register_object(obj, 'update')
                self._log("Updated "+str(obj))

        # We need to delete relations first
        for obj in self._delete:
            if self.metadata_map.is_relationship(obj):
                uow.register_object(obj, 'delete')
                self._log("Deleted "+str(obj))
        for obj in self._delete:
            if self.metadata_map.is_node(obj):
                uow.register_object(obj, 'delete')
                self._log("Deleted "+str(obj))

        return self


    def _log(self, message, level=10):
        if self.logger is None:
            return self
        self.logger.log(level, message)