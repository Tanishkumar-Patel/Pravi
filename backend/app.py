import os
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

from models import db, User, Family, Member, Scheme, Application, Benefit
from eligibility import evaluate_eligibility

# Setup
load_dotenv()
app = Flask(__name__)
CORS(app)

# Database Configuration (Will pull from .env later)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'development_secret_key')

db.init_app(app)

# --- MIDDLEWARE ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        try:
            token = token.split(" ")[1] if " " in token else token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
        except Exception as e:
            return jsonify({'message': 'Invalid token'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# --- AUTH ROUTES ---
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 400
    
    user = User(
        email=data['email'],
        password_hash=generate_password_hash(data['password']),
        role=data.get('role', 'CITIZEN')
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registered successfully', 'user_id': str(user.user_id)}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    token = jwt.encode({
        'user_id': str(user.user_id),
        'role': user.role,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token, 'role': user.role, 'family_id': str(user.family_id) if user.family_id else None})

# --- CITIZEN: FAMILY ROUTES ---
@app.route('/api/family', methods=['POST'])
@token_required
def create_family(current_user):
    data = request.get_json()
    family = Family(
        address=data['address'],
        district=data['district'],
        taluka=data['taluka'],
        village=data['village'],
        annual_income=data.get('annual_income', 0.0)
    )
    db.session.add(family)
    db.session.flush()
    current_user.family_id = family.family_id
    db.session.commit()
    return jsonify({'family_id': str(family.family_id)}), 201

@app.route('/api/family/members', methods=['POST'])
@token_required
def add_member(current_user):
    data = request.get_json()
    member = Member(
        family_id=current_user.family_id,
        full_name=data['full_name'],
        date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
        gender=data['gender'],
        relationship_to_head=data['relationship_to_head'],
        occupation=data.get('occupation'),
        education=data.get('education')
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({'member_id': str(member.member_id)}), 201

# --- SCHEMES & APPLICATIONS ---
@app.route('/api/schemes', methods=['GET'])
def get_schemes():
    schemes = Scheme.query.filter_by(is_active=True).all()
    return jsonify([{
        'scheme_id': str(s.scheme_id),
        'scheme_name': s.scheme_name,
        'beneficiary_type': s.beneficiary_type
    } for s in schemes])

@app.route('/api/applications', methods=['POST'])
@token_required
def apply_scheme(current_user):
    data = request.get_json()
    scheme = Scheme.query.get_or_404(data['scheme_id'])
    family = Family.query.get_or_404(current_user.family_id)
    member = Member.query.get(data.get('member_id')) if data.get('member_id') else None

    # Check Eligibility Engine
    eval_res = evaluate_eligibility(scheme, family, member)
    if not eval_res['eligible']:
        return jsonify({'message': 'Not eligible', 'reasons': eval_res['reasons']}), 400

    application = Application(
        scheme_id=scheme.scheme_id,
        family_id=family.family_id,
        member_id=member.member_id if member else None
    )
    db.session.add(application)
    db.session.commit()
    return jsonify({'message': 'Applied successfully'}), 201

if __name__ == '__main__':
    # We will let Supabase handle table creation, so we don't strictly need db.create_all() here.
    app.run(debug=True, port=5000)