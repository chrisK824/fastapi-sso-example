from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String)
    password = Column(String, nullable=True)
    provider = Column(String, default="local", nullable=True)
    fullname = Column(String, nullable=True)
    register_date = Column(DateTime, default=func.now())
    __table_args__ = (UniqueConstraint('email', 'provider', name='unique_email_per_provider'),)

    @property
    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
