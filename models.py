from flask_sqlalchemy import SQLAlchemy
from app import app
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String[32],unique=True,nullable=False)
    passhash = db.Column(db.String[512], nullable=False)
    name = db.Column(db.String[64], nullable=True)
    email = db.Column(db.String[64], nullable=True)

    is_admin = db.Column(db.Boolean, nullable=False, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        self.passhash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.passhash, password)

class Book(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String[64], nullable=False)
    author = db.Column(db.String[64], nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'),nullable=False)
    date_issued = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)

class Section(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String[32],unique=True,nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    desc = db.Column(db.String[512], nullable=True)   
    # Foreign Key Relation
    books = db.relationship('Book',backref='section',lazy=True)

class Library(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    return_date = db.Column(db.Date, db.ForeignKey('book.return_date'),nullable=False)

#If Tables dont exist Create them
with app.app_context():
    db.create_all()
    # Creating Admin
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', password='admin', name='admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()