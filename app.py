from flask import Flask, render_template
from database import db, Admin
from werkzeug.security import generate_password_hash

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

if __name__ == "__main__":
    app.run(debug=True)