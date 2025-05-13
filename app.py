import datetime
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite').replace('postgres://', 'postgresql://')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    is_manager = db.Column(db.Boolean, default=False)

class EmployeePerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    kpi_1 = db.Column(db.Integer)
    kpi_2 = db.Column(db.Integer)
    kpi_3 = db.Column(db.Integer)
    comments = db.Column(db.Text)
    date = db.Column(db.Date)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_manager:
        performances = EmployeePerformance.query.all()
        employees = User.query.filter_by(is_manager=False).all()
        return render_template('manager_dashboard.html', performances=performances, employees=employees)
    else:
        performances = EmployeePerformance.query.filter_by(employee_id=current_user.id).all()
        return render_template('employee_dashboard.html', performances=performances)

@app.route('/add_performance', methods=['POST'])
@login_required
def add_performance():
    if current_user.is_manager:
        employee_id = request.form.get('employee_id')
        kpi_1 = request.form.get('kpi_1')
        kpi_2 = request.form.get('kpi_2')
        kpi_3 = request.form.get('kpi_3')
        comments = request.form.get('comments')
        
        new_performance = EmployeePerformance(
            employee_id=employee_id,
            kpi_1=kpi_1,
            kpi_2=kpi_2,
            kpi_3=kpi_3,
            comments=comments,
            date=datetime.now().date()
        )
        
        db.session.add(new_performance)
        db.session.commit()
        flash('Performance added successfully')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)