import datetime
from sqlalchemy import (
    Column,
    Integer,
    Text,
    DateTime,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class Quip(Base):
    __tablename__ = 'quips'
    id = Column(Integer, primary_key=True)
    quipped_text = Column(Text)
    source = Column(Text)
    submitter = Column(Text)
    source_date = Column(DateTime, default=datetime.datetime.utcnow)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
     
