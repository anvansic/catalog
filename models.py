from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(30), nullable=False)


class Book(Base):
    __tablename__ = 'book'

    id = Column(Integer, primary_key=True)
    title = Column(String(72), nullable=False)
    author = Column(String(30), nullable=False)
    year = Column(Integer, nullable=False)
    genre = Column(String(25), nullable=False)
    synopsis = Column(String(200), nullable=False)
    creator_id = Column(Integer, ForeignKey('user.id'))
    creator = relationship(User)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'genre': self.genre,
            'synopsis': self.synopsis,
            'creator_id': self.creator_id
        }


engine = create_engine('sqlite:///books.db')
Base.metadata.create_all(engine)
