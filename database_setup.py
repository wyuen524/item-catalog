import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# Stores user information
class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False, unique=True)


# Stores category information
class Weapon(Base):
    __tablename__ = 'weapon'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    details = relationship('ItemInfo', cascade='all, delete-orphan')
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }


# Stores item information
class ItemInfo(Base):
    __tablename__ = 'details'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    damage = Column(String(8))
    dps = Column(String(8))
    weapon_id = Column(Integer, ForeignKey('weapon.id'))
    weapon = relationship(Weapon)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'damage': self.damage,
            'dps': self.dps,
        }


engine = create_engine('sqlite:///fortniteitems.db')

Base.metadata.create_all(engine)
