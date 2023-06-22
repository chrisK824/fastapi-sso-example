from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=True)
    provider = Column(String, default="local", nullable=True)
    fullname = Column(String, nullable=True)
    register_date = Column(DateTime, default=func.now())

    @property
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
