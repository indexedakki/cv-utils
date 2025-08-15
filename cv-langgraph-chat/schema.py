from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, JSON

# Shared metadata for all table definitions
metadata = MetaData()

# Users table schema
def define_candidate_table():
    return Table(
        'candidates', metadata,
        Column('user_id', Integer, primary_key=True, autoincrement=True),
        Column('name', String(100), nullable=False),
        Column('email', String(100), nullable=False, unique=True),
        Column('phone', String(15), nullable=False),
        Column('linkedin', String(50), nullable=True),
        Column('location', String(100), nullable=False),
        Column('role', String(50), nullable=False),
        Column('experience_years', Integer, nullable=False),
        Column('skills', JSON, nullable=True),
        Column('achievements', JSON, nullable=True),
        Column('career_gap', JSON, nullable=True),
        Column('present_employer', String(100), nullable=True),
        Column('resume_metadata', String(255), nullable=True),
        Column('created_at', DateTime, nullable=False),
    )
