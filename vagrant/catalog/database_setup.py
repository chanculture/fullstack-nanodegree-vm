import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    profile_picture = Column(String(250))
    date_joined = Column(DateTime, default=datetime.datetime.utcnow)

# We added this serialize function to be able to send JSON objects in a
# serializable format

    @property
    def serialize(self):
        return {
            'name': self.name,
            'email': self.email,
            'profile_picture': self.profile_picture,
            'date_joined': self.date_joined,
            'id': self.id,
        }

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }

class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=True)
    date_added = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer,ForeignKey('user.id'))
    user = relationship(User)
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'date_added': self.date_added,
            'category': self.category.name,
            'user': self.user.name,
        }

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)