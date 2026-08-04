from flask import Flask, render_template, redirect, url_for, request, session, flash
from database import db, Admin, Staff, User, Trek, Booking
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
    total_treks = Trek.query.count()
    total_users = User.query.count()
    total_staff = Staff.query.count()
    total_bookings = Booking.query.count()
    return render_template('admin/dashboard.html',
        total_treks=total_treks,
        total_users=total_users,
        total_staff=total_staff,
        total_bookings=total_bookings)

@app.route('/staff/dashboard')
def staff_dashboard():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    treks = Trek.query.filter_by(assigned_staff_id=session['user_id']).all()
    return render_template('staff/dashboard.html', treks=treks)

@app.route('/admin/treks')
def admin_treks():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    treks = Trek.query.all()
    return render_template('admin/treks.html', treks=treks)

@app.route('/admin/treks/add', methods=['GET', 'POST'])
def admin_add_trek():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    from forms import TrekForm
    from datetime import datetime
    form = TrekForm()
    if form.validate_on_submit():
        start = datetime.strptime(form.start_date.data, '%d/%m/%Y') if form.start_date.data else None
        end = datetime.strptime(form.end_date.data, '%d/%m/%Y') if form.end_date.data else None
        trek = Trek(
            name=form.name.data,
            location=form.location.data,
            difficulty=form.difficulty.data,
            duration=int(form.duration.data),
            available_slots=int(form.available_slots.data),
            start_date=start,
            end_date=end,
            status='open'
        )
        db.session.add(trek)
        db.session.commit()
        flash('trek added successfully.', 'success')
        return redirect(url_for('admin_treks'))
    return render_template('admin/add_trek.html', form=form)

@app.route('/admin/treks/delete/<int:trek_id>')
def admin_delete_trek(trek_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    trek = Trek.query.get_or_404(trek_id)
    db.session.delete(trek)
    db.session.commit()
    flash('trek deleted.', 'success')
    return redirect(url_for('admin_treks'))

@app.route('/admin/treks/edit/<int:trek_id>', methods=['GET', 'POST'])
def admin_edit_trek(trek_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    from forms import TrekForm
    from datetime import datetime
    trek = Trek.query.get_or_404(trek_id)
    form = TrekForm()
    if form.validate_on_submit():
        trek.name = form.name.data
        trek.location = form.location.data
        trek.difficulty = form.difficulty.data
        trek.duration = int(form.duration.data)
        trek.available_slots = int(form.available_slots.data)
        trek.start_date = datetime.strptime(form.start_date.data, '%d/%m/%Y') if form.start_date.data else None
        trek.end_date = datetime.strptime(form.end_date.data, '%d/%m/%Y') if form.end_date.data else None
        db.session.commit()
        flash('trek updated successfully.', 'success')
        return redirect(url_for('admin_treks'))
    form.name.data = trek.name
    form.location.data = trek.location
    form.difficulty.data = trek.difficulty
    form.duration.data = str(trek.duration)
    form.available_slots.data = str(trek.available_slots)
    return render_template('admin/add_trek.html', form=form)

@app.route('/admin/staff')
def admin_staff():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    staff_list = Staff.query.all()
    return render_template('admin/staff.html', staff_list=staff_list)

@app.route('/admin/staff/approve/<int:staff_id>')
def approve_staff(staff_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    staff = Staff.query.get_or_404(staff_id)
    staff.status = 'approved'
    db.session.commit()
    flash('staff approved.', 'success')
    return redirect(url_for('admin_staff'))

@app.route('/admin/staff/blacklist/<int:staff_id>')
def blacklist_staff(staff_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    staff = Staff.query.get_or_404(staff_id)
    staff.status = 'blacklisted'
    db.session.commit()
    flash('staff blacklisted.', 'danger')
    return redirect(url_for('admin_staff'))

@app.route('/admin/users')
def admin_users():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/blacklist/<int:user_id>')
def blacklist_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    user.status = 'blacklisted'
    db.session.commit()
    flash('user blacklisted.', 'danger')
    return redirect(url_for('admin_users'))

@app.route('/admin/users/activate/<int:user_id>')
def activate_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    user.status = 'active'
    db.session.commit()
    flash('user activated.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/bookings')
def admin_bookings():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    bookings = Booking.query.all()
    return render_template('admin/bookings.html', bookings=bookings)

@app.route('/admin/treks/assign/<int:trek_id>', methods=['GET', 'POST'])
def assign_staff(trek_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    trek = Trek.query.get_or_404(trek_id)
    staff_list = Staff.query.filter_by(status='approved').all()
    if request.method == 'POST':
        staff_id = request.form.get('staff_id')
        trek.assigned_staff_id = int(staff_id)
        db.session.commit()
        flash('staff assigned successfully.', 'success')
        return redirect(url_for('admin_treks'))
    return render_template('admin/assign_staff.html', trek=trek, staff_list=staff_list)

@app.route('/staff/trek/<int:trek_id>', methods=['GET', 'POST'])
def staff_manage_trek(trek_id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != session['user_id']:
        flash('you are not assigned to this trek.', 'danger')
        return redirect(url_for('staff_dashboard'))
    if request.method == 'POST':
        trek.available_slots = int(request.form.get('available_slots'))
        trek.status = request.form.get('status')
        db.session.commit()
        flash('trek updated successfully.', 'success')
        return redirect(url_for('staff_manage_trek', trek_id=trek_id))
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    return render_template('staff/manage_trek.html', trek=trek, bookings=bookings)

@app.route('/user/dashboard')
def user_dashboard():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    search = request.args.get('search', '')
    difficulty = request.args.get('difficulty', '')
    query = Trek.query.filter_by(status='open')
    if search:
        query = query.filter(Trek.name.contains(search) | Trek.location.contains(search))
    if difficulty:
        query = query.filter_by(difficulty=difficulty)
    treks = query.all()
    return render_template('user/dashboard.html', treks=treks, search=search, difficulty=difficulty)

@app.route('/user/trek/<int:trek_id>')
def user_trek_detail(trek_id):
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    trek = Trek.query.get_or_404(trek_id)
    already_booked = Booking.query.filter_by(user_id=session['user_id'], trek_id=trek_id).first()
    return render_template('user/trek_detail.html', trek=trek, already_booked=already_booked)

@app.route('/user/book/<int:trek_id>')
def user_book_trek(trek_id):
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    trek = Trek.query.get_or_404(trek_id)
    if trek.status != 'open':
        flash('this trek is not open for booking.', 'danger')
        return redirect(url_for('user_dashboard'))
    if trek.available_slots <= 0:
        flash('no slots available for this trek.', 'danger')
        return redirect(url_for('user_dashboard'))
    already_booked = Booking.query.filter_by(user_id=session['user_id'], trek_id=trek_id).first()
    if already_booked:
        flash('you have already booked this trek.', 'warning')
        return redirect(url_for('user_dashboard'))
    booking = Booking(user_id=session['user_id'], trek_id=trek_id)
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    flash('trek booked successfully!', 'success')
    return redirect(url_for('user_bookings'))

@app.route('/user/bookings')
def user_bookings():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('user/my_bookings.html', bookings=bookings)

@app.route('/user/history')
def user_history():
    if session.get('role') != 'user':
        return redirect(url_for('login'))
    bookings = Booking.query.filter_by(user_id=session['user_id']).all()
    return render_template('user/history.html', bookings=bookings)

if __name__ == "__main__":
    app.run(debug=True)