import abc

from swagger_server.__main__ import db
from swagger_server.models.base_model_ import Model


class BaseModel(db.Model):
    """Base model class that define all the common methods to all the models.

    This includes all the transaction management methods, all the mapping
    methods to the swagger models and all the common query methods like
    get_all.

    :parent: db.Model
    """

    __abstract__ = True
    """The __abstract__ attribute will prevent sql alchemy from creating a
    table for this class.
    """

    def commit(self):
        """Commit a transaction"""
        db.session.commit()

    def rollback(self):
        """rollback the transactions"""
        db.session.rollback()

    def add(self):
        """Add an Insert in the transaction list"""
        db.session.add(self)

    def flush(self):
        """Sends to the database the operations in the transaction list"""
        db.session.flush()

    def update(self, updated_model: "BaseModel"):
        """Add an Update of the not null fields in the transaction list"""
        updated_model_dict = updated_model.__dict__
        for key in updated_model_dict.keys():
            if key != "_sa_instance_state":
                value = updated_model_dict[key]
                if value:
                    self.__setattr__(key, value)

    def delete(self):
        """Add a Delete in the transaction list"""
        db.session.delete(self)

    @classmethod
    @abc.abstractmethod
    def from_obj(cls, obj: Model) -> "BaseModel":
        """Create a new instance of the DAO based on an instance

        :param obj: Edition

        :return: EditionModel
        """
        pass

    @abc.abstractmethod
    def to_obj(self) -> "Model":
        """Create a new instance based on the data from the DAO
        instance

        :return: Edition
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get_all(cls, filters: dict = {}):
        """Get the list of items

        :param filters: list

        :return list
        """
        pass

    @classmethod
    @abc.abstractmethod
    def get(cls, item_id: int):
        """Get a single item by it's id

        :param item_id: int

        :return item
        """
        pass
