from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase


class BaseMeta(AsyncAttrs, DeclarativeBase.__class__, ABC.__class__):
    pass

class Base(ABC, AsyncAttrs, DeclarativeBase, metaclass=BaseMeta):
    __abstract__ = True

    @abstractmethod
    def get_data():
        pass

    @abstractmethod
    def add_data():
        pass
    
