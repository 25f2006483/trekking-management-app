from flask import Flask, render_template, redirect, url_for, request, session, flash
from database import db, Admin, Staff, User
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'trekking-secret-key'

db.init_app(app)

def create_default_admin():
    admin = Admin.query.filter_by(username='admin').first()
    if admin is None:
        hashed = generate_password_hash('admin123')
        default_admin = Admin(username='admin', password_hash=hashed)
        db.session.add(default_admin)
        db.session.commit()
        print("default admin created.")
    else:
        print("admin already exists.")

with app.app_context():
    db.create_all()
    create_default_admin()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.role.data == 'user':
            existing = User.query.filter_by(email=form.email.data).first()
            if existing:
                flash('email already registered. please login.', 'danger')
                return redirect(url_for('register'))
            hashed = generate_password_hash(form.password.data)
            new_user = User(
                name=form.name.data,
                email=form.email.data,
                contact=form.contact.data,
                password_hash=hashed
            )
            db.session.add(new_user)
            db.session.commit()
            flash('registration successful. please login.', 'success')
            return redirect(url_for('login'))

        elif form.role.data == 'staff':
            existing = Staff.query.filter_by(email=form.email.data).first()
            if existing:
                flash('email already registered. please login.', 'danger')
                return redirect(url_for('register'))
            hashed = generate_password_hash(form.password.data)
            new_staff = Staff(
                name=form.name.data,
                email=form.email.data,
                contact=form.contact.data,
                password_hash=hashed
            )
            db.session.add(new_staff)
            db.session.commit()
            flash('registration successful. wait for admin approval.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        role = form.role.data
        password = form.password.data

        if role == 'admin':
            admin = Admin.query.filter_by(username=form.username.data).first()
            if admin and check_password_hash(admin.password_hash, password):
                session['user_id'] = admin.id
                session['role'] = 'admin'
                session['name'] = admin.username
                return redirect(url_for('admin_dashboard'))
            else:
                flash('invalid admin credentials.', 'danger')

        elif role == 'staff':
            staff = Staff.query.filter_by(email=form.username.data).first()
            if staff and check_password_hash(staff.password_hash, password):
                if staff.status == 'pending':
                    flash('your account is pending admin approval.', 'warning')
                elif staff.status == 'blacklisted':
                    flash('your account has been blacklisted.', 'danger')
                else:
                    session['user_id'] = staff.id
                    session['role'] = 'staff'
                    session['name'] = staff.name
                    return redirect(url_for('staff_dashboard'))
            else:
                flash('invalid staff credentials.', 'danger')

        elif role == 'user':
            user = User.query.filter_by(email=form.username.data).first()
            if user and check_password_hash(user.password_hash, password):
                if user.status == 'blacklisted':
                    flash('your account has been blacklisted.', 'danger')
                else:
                    session['user_id'] = user.id
                    session['role'] = 'user'
                    session['name'] = user.name
                    return redirect(url_for('user_dashboard'))
            else:
                flash('invalid credentials.', 'danger')

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin/dashboard.html')

@app.route('/staff/dashboard')
def staff_dashboard():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    return render_template('staff/dashboard.html')

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    return render_template('user/dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)