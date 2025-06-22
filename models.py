# models.py
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ATSResult(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True)
    job_description = Column(Text)
    resume_filename = Column(String)
    analysis_type = Column(String)  # summary / match / improvement
    result = Column(Text)
