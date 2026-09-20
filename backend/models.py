import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID, JSONB

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='CITIZEN')
    family_id = db.Column(UUID(as_uuid=True), db.ForeignKey('families.family_id'), nullable=True)

class Family(db.Model):
    __tablename__ = 'families'
    family_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_head_member_id = db.Column(UUID(as_uuid=True), nullable=True)
    address = db.Column(db.Text, nullable=False)
    district = db.Column(db.String(100), nullable=False)
    taluka = db.Column(db.String(100), nullable=False)
    village = db.Column(db.String(100), nullable=False)
    annual_income = db.Column(db.Numeric(12, 2), nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = db.relationship('Member', backref='family', lazy=True, foreign_keys='Member.family_id')

class Member(db.Model):
    __tablename__ = 'members'
    member_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    family_id = db.Column(UUID(as_uuid=True), db.ForeignKey('families.family_id'), nullable=False)
    full_name = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    relationship_to_head = db.Column(db.String(50), nullable=False)
    occupation = db.Column(db.String(100))
    education = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Scheme(db.Model):
    __tablename__ = 'schemes'
    scheme_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    beneficiary_type = db.Column(db.String(20), nullable=False) # 'MEMBER' or 'FAMILY'
    eligibility_criteria = db.Column(JSONB, default={})
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Application(db.Model):
    __tablename__ = 'applications'
    application_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scheme_id = db.Column(UUID(as_uuid=True), db.ForeignKey('schemes.scheme_id'), nullable=False)
    family_id = db.Column(UUID(as_uuid=True), db.ForeignKey('families.family_id'), nullable=False)
    member_id = db.Column(UUID(as_uuid=True), db.ForeignKey('members.member_id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='PENDING') # PENDING, APPROVED, REJECTED
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Benefit(db.Model):
    __tablename__ = 'benefits'
    benefit_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id = db.Column(UUID(as_uuid=True), db.ForeignKey('applications.application_id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='ACTIVE') # ACTIVE, EXPIRED, REVOKED
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)