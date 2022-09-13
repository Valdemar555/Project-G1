from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class Book(Base):

	__tablename__ = 'books'


	id = Column(Integer, primary_key=True, autoincrement=True)
	link = Column(String(512), index=True, unique=True, nullable=False)
	title = Column(String(512))
	author = Column(String(128))
	avialability = Column(String(128))
	price = Column(Integer)
	special_price = Column(Integer)


	def __repr__(self):
		return f'{self.link}||{self.title}||{self.author}||{self.avialability}||{self.price}||{self.special_price}'


	def __str__(self):
		return self.__repr__()



async def pg_context(app):
    conf = app['config']['mysql']
    url_db = f"mysql+mysqlconnector://{conf['user']}:{conf['password']}@{conf['host']}/{conf['database']}?charset=utf8"
    DBSession = sessionmaker(bind=create_engine(url_db))
    session = DBSession()
    app['db_session'] = session
    yield
    app['db_session'].close()
