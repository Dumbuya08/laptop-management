from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hui6742guy93rru9387tyg3ry7tyr98'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///laptops.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

# Models for Users and Laptops
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), nullable=False)

class Laptop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(100), unique=True, nullable=False)
    model = db.Column(db.String(100), nullable=False)
    allocated_to = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=False)
    issue_reported = db.Column(db.String(255), nullable=True)
    allocation_date = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            return "Invalid login details"
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        laptops = Laptop.query.all()
    else:
        laptops = Laptop.query.filter_by(allocated_to=current_user.username).all()
    return render_template('dashboard.html', laptops=laptops)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_laptop', methods=['GET', 'POST'])
@login_required
def add_laptop():
    if current_user.role != 'admin':
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        serial_number = request.form['serial_number']
        model = request.form['model']
        new_laptop = Laptop(serial_number=serial_number, model=model, status='available')
        db.session.add(new_laptop)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_laptop.html')

@app.route('/edit_laptop/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_laptop(id):
    laptop = Laptop.query.get(id)
    if request.method == 'POST':
        laptop.serial_number = request.form['serial_number']
        laptop.model = request.form['model']
        laptop.status = request.form['status']
        laptop.allocated_to = request.form['allocated_to']
        laptop.issue_reported = request.form['issue_reported']
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('edit_laptop.html', laptop=laptop)

@app.route('/generate_report')
@login_required
def generate_report():
    laptops = Laptop.query.all()
    report = {}
    for laptop in laptops:
        report[laptop.serial_number] = {
            'allocated_to': laptop.allocated_to,
            'status': laptop.status,
            'issue_reported': laptop.issue_reported,
            'allocation_date': laptop.allocation_date.strftime('%Y-%m-%d %H:%M')
        }
    return jsonify(report)

if __name__ == '__main__':
    app.run(debug=True)
