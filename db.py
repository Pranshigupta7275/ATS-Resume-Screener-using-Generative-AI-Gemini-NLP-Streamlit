# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, ATSResult

# Setup DB connection
engine = create_engine('sqlite:///ats_results.db', echo=False)

# Create table (only if not exists)
Base.metadata.create_all(engine)

# Setup session
Session = sessionmaker(bind=engine)
session = Session()

# Optional delete function
def delete_all_results():
    session.query(ATSResult).delete()
    session.commit()
