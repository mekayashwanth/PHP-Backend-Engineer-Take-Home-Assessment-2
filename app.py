from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loan_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    is_lender = db.Column(db.Boolean, default=False)
    loans_as_lender = db.relationship('Loan', foreign_keys='Loan.lender_id', backref='lender', lazy='dynamic')
    loans_as_borrower = db.relationship('Loan', foreign_keys='Loan.borrower_id', backref='borrower', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    lender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            print(f"Authorization Header: {auth_header}")  # Debugging line
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                return jsonify({'message': 'Invalid token format'}), 401
        else:
            return jsonify({'message': 'Token is missing!'}), 401

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.filter_by(id=data['id']).first()
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'message': f'Invalid token: {str(e)}'}), 401

        return func(current_user, *args, **kwargs)
    return decorated

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User(username=data['username'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'User created successfully!'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid username or password'}), 401

    token = jwt.encode({'id': user.id, 'exp': datetime.utcnow() + timedelta(minutes=30)}, app.config['SECRET_KEY'], algorithm='HS256')
    print(f"Generated Token: {token}")  # Debugging line
    return jsonify({'token': token})

@app.route('/loans', methods=['GET'])
def get_loans():
    loans = Loan.query.all()
    return jsonify([{'id': loan.id, 'amount': loan.amount, 'status': loan.status, 'created_at': loan.created_at.isoformat(), 'lender': loan.lender.username, 'borrower': loan.borrower.username} for loan in loans])

@app.route('/loans', methods=['POST'])
@token_required
def create_loan(current_user):
    data = request.get_json()
    lender = User.query.filter_by(username=data['lender']).first()
    borrower = User.query.filter_by(username=data['borrower']).first()

    if not lender or not borrower:
        return jsonify({'message': 'Invalid lender or borrower'}), 400

    loan = Loan(amount=data['amount'], lender=lender, borrower=borrower)
    db.session.add(loan)
    db.session.commit()
    return jsonify({'id': loan.id, 'amount': loan.amount, 'status': loan.status, 'created_at': loan.created_at.isoformat(), 'lender': loan.lender.username, 'borrower': loan.borrower.username}), 201

@app.route('/loans/<int:loan_id>', methods=['PUT'])
@token_required
def update_loan(current_user, loan_id):
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    if loan.lender_id != current_user.id:
        return jsonify({'message': 'Only the original lender can edit this loan'}), 403

    data = request.get_json()
    loan.amount = data['amount']
    loan.status = data['status']
    db.session.commit()
    return jsonify({'id': loan.id, 'amount': loan.amount, 'status': loan.status, 'created_at': loan.created_at.isoformat(), 'lender': loan.lender.username, 'borrower': loan.borrower.username})

@app.route('/loans/<int:loan_id>', methods=['DELETE'])
@token_required
def delete_loan(current_user, loan_id):
    loan = Loan.query.get(loan_id)
    if not loan:
        return jsonify({'message': 'Loan not found'}), 404

    if loan.lender_id != current_user.id:
        return jsonify({'message': 'Only the original lender can delete this loan'}), 403

    db.session.delete(loan)
    db.session.commit()
    return jsonify({'message': 'Loan deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
