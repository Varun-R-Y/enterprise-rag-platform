from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy database models.
    Inherits from DeclarativeBase, following the SQLAlchemy 2.0 standard style.
    
    All application models must inherit from this class to participate in metadata collection.
    """
    pass
