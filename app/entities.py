# System imports
import datetime
# Libs imports
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.types import DateTime
# from sqlalchemy.orm import relationship

from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, index=True)
    website = Column(String)
    city = Column(String)
    country = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    # users = relationship("User", back_populates="company")


class Planning(Base):
    __tablename__ = "plannings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    company_id = Column(Integer, ForeignKey("companies.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    # company = relationship("Company", back_populates="plannings")
    # users = relationship("User", back_populates="planning")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    start_date = Column(DateTime, default=datetime.datetime.utcnow)
    end_date = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    planning_id = Column(Integer, ForeignKey("plannings.id"))
    # planning = relationship("Planning", back_populates="events")
    # users = relationship("User", back_populates="events")
