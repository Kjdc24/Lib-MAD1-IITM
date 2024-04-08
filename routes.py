from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Book, Section, Request
from functools import wraps
from app import app
import datetime

def auth_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session:
            flash('Please Login.')
            return redirect(url_for('login'))
        return func(*args,**kwargs)
    return inner

def admin_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session:
            flash('Please Login.')
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user.is_admin:
            flash('Not Authorized')
            return redirect(url_for('index'))
        return func(*args,**kwargs)
    return inner

@app.route('/')
@auth_required
def index():
    user = User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin'))
    else:
        return render_template('index.html', user = user)
    
@app.route('/admin')
@admin_required
def admin():
    user = User.query.get(session['user_id'])
    if not user.is_admin:
        flash('Not Authorized')
        return redirect(url_for('index'))
    return render_template('admin.html', user=user, sections = Section.query.all())

@app.route('/profile')
@auth_required
def profile():
    return render_template('profile.html', user = User.query.get(session['user_id']))

@app.route('/profile', methods=['POST'])
@auth_required
def profile_post():
    user = User.query.get(session['user_id'])
    username = request.form.get('username')
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    cpassword = request.form.get('cpassword')
    if username == '' or password == '' or cpassword == '':
        flash('Username and Password cannot be empty')
        return redirect(url_for('profile'))
    if not user.check_password(cpassword):
        flash('Password Incorrect')
        return redirect(url_for('profile'))
    if User.query.filter_by(username=username).first() and username != user.username:
        flash('Username already Exists')
        return redirect(url_for('profile'))
    user.username = username
    user.name = name
    user.email = email
    user.password = password
    db.session.commit()
    flash('Profile Updated.')
    return redirect(url_for('profile'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == '' or password == '':
        flash('Username and Password cannot be empty')
        return redirect(url_for('register'))
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('Please Check Your Login Credentials and Try again')
        return redirect(url_for('login'))
    if not user.check_password(password):
        flash('Invalid Credentials and Try again')
        return redirect(url_for('login'))
    #Login Successful
    session['user_id'] = user.id
    return redirect(url_for('index'))

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
    username = request.form.get('username')
    password = request.form.get('password')
    name = request.form.get('name')
    email = request.form.get('email')
    if username == '' or password == '':
        flash('Username and Password cannot be empty')
        return redirect(url_for('register'))
    if User.query.filter_by(username=username).first():
        flash('Username already Exists')
        return redirect(url_for('register'))
    user = User(username=username,password=password,name=name,email=email)
    db.session.add(user)
    db.session.commit()
    flash('User Registered Successfully')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/mybooks')
@auth_required
def mybooks():
    return "    "

@app.route('/requests')
@auth_required
def requests():
    return "    "

@app.route('/section/add')
@admin_required
def add_section():
    return render_template('section/add.html', user = User.query.get(session['user_id']))

@app.route('/section/add', methods=['POST'])
@admin_required
def add_section_post():
    name = request.form.get('name')
    date_created = request.form.get('date_created')
    # You can add code here to validate and format the date if needed
    try:
        date_created = datetime.datetime.strptime(date_created, '%Y-%m-%d').date()
    except ValueError:
        flash('Invalid date format. Please use YYYY-MM-DD format.')
        return redirect(url_for('add_section'))
    desc = request.form.get('desc')
    if name == '':
        flash('Section Name cannot be empty')
        return redirect(url_for('add_section'))
    if len(name) > 64:
        flash('Section Name cannot be more than 32 characters')
        return redirect(url_for('add_section'))
    section = Section(name=name,date_created=date_created,desc=desc)
    db.session.add(section)
    db.session.commit()
    flash('Section Added Successfully')
    return redirect(url_for('admin'))

@app.route('/section/<int:id>/show')
@admin_required
def show_section(id):
    return render_template('section/show.html',user = User.query.get(session['user_id']),section = Section.query.get(id))

@app.route('/section/<int:id>/edit')
@admin_required
def edit_section(id):
    return render_template('section/edit.html',user = User.query.get(session['user_id']),section = Section.query.get(id))

@app.route('/section/<int:id>/delete')
@admin_required
def delete_section(id):
    section = Section.query.get(id)
    if not section:
        flash('Section Not Found')
        return redirect(url_for('admin'))
    return render_template('section/delete.html',user = User.query.get(session['user_id']),section = section)

@app.route('/section/<int:id>/delete', methods=['POST'])
@admin_required
def delete_section_post(id):
    section = Section.query.get(id)
    if not section:
        flash('Section Not Found')
        return redirect(url_for('admin'))
    db.session.delete(section)
    db.session.commit()
    flash('Section Deleted Successfully')
    return redirect(url_for('admin'))

@app.route('/section/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_section_post(id):
    section = Section.query.get(id)
    if request.method == 'POST':
        section.name = request.form.get('name')
        date_created = request.form.get('date_created')
        # You can add code here to validate and format the date if needed
        try:
            date_created = datetime.datetime.strptime(date_created, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD format.')
            return redirect(url_for('edit_section'))
        section.date_created = date_created
        section.desc = request.form.get('desc')
        db.session.commit()
        flash('Section Updated Successfully', 'success')
        return redirect(url_for('admin'))
    
@app.route('/section/add-books')
@admin_required
def add_books():
    section_id = -1
    args = request.args
    if 'section_id' in args:
        if Section.query.get(int(args.get('section_id'))):
            section_id = int(args.get('section_id'))
    return render_template('book/add.html', user = User.query.get(session['user_id']),section_id = section_id ,sections = Section.query.all())

@app.route('/section/add-books', methods=['POST'])
@admin_required
def add_books_post():
    title = request.form.get('title')
    author = request.form.get('author')
    section = request.form.get('section')
    if title == '' or author == '' or section == '':
        flash('Fields cannot be empty')
        return redirect(url_for('add_books'))
    if not Section.query.get(section):
        flash('Section Not Found')
        return redirect(url_for('add_books'))
    book = Book(title=title,author=author,section_id=section)
    db.session.add(book)
    db.session.commit()
    flash('Book Added Successfully')
    return redirect(url_for('show_section', id=section))

@app.route('/book/<int:book_id>/edit')
@admin_required
def edit_book(book_id):
    return render_template('book/edit.html',user = User.query.get(session['user_id']),
                           book = Book.query.get(book_id),sections = Section.query.all())

@app.route('/book/<int:book_id>/edit', methods=['POST'])
@admin_required
def edit_book_post(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash('Book Not Found')
        return redirect(url_for('show_section', id=book.section_id))
    book.title = request.form.get('title')
    book.author = request.form.get('author')
    db.session.commit()
    flash('Book Updated Successfully')
    return redirect(url_for('show_section', id=book.section_id))

@app.route('/book/<int:book_id>/delete')
@admin_required
def delete_book(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash('Book Not Found')
        return redirect(url_for('show_section', id=book.section_id))
    return render_template('book/delete.html',user = User.query.get(session['user_id']),book = book)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
@admin_required
def delete_book_post(book_id):
    book = Book.query.get(book_id)
    if not book:
        flash('Book Not Found')
        return redirect(url_for('show_section', id=book.section_id))
    db.session.delete(book)
    db.session.commit()
    flash('Book Deleted Successfully')
    return redirect(url_for('show_section', id=book.section_id))
