from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, FileField, SubmitField, DecimalField
from wtforms.validators import DataRequired, NumberRange
from werkzeug.utils import secure_filename
import os
import mysql.connector

os.environ['FLASK_SKIP_DOTENV'] = '1'  # Disable automatic .env loading

app = Flask(__name__)
app.config.from_object('config.Config')

db = SQLAlchemy(app)

# Database Models
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    category = db.relationship('Category', backref=db.backref('products', lazy=True))
    image_filename = db.Column(db.String(200), nullable=True)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    discounted_price = db.Column(db.DECIMAL(10, 2), nullable=True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(500), nullable=False)

# Form for Product Management
class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    image = FileField('Product Image')
    price = DecimalField('Price ($)', validators=[DataRequired(), NumberRange(min=0, message="Price must be non-negative")])
    discounted_price = DecimalField('Discounted Price ($)', validators=[NumberRange(min=0, message="Discounted price must be non-negative")])
    submit = SubmitField('Save Product')

# Template Context Processor
@app.context_processor
def inject_categories():
    return dict(categories=Category.query.order_by(Category.name).all())

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/products/<category_slug>')
def category_products(category_slug):
    category = Category.query.filter_by(slug=category_slug).first_or_404()
    return render_template('category.html', category=category)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if query:
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
        return render_template('search.html', query=query, products=products)
    return render_template('search.html', query='', products=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Attempting login with username: {username}, password: {password}")
        user = User.query.filter_by(username=username).first()
        print(f"User found: {user}")
        if user:
            print(f"Stored hash: {user.password}")
            print(f"Password check result: {check_password_hash(user.password, password)}")
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            print(f"Session set: {session}")
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_products'))
        flash('Invalid credentials', 'error')
    return render_template('login.html')

@app.route('/admin/products', methods=['GET', 'POST'])
def admin_products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    products = Product.query.all()
    categories = Category.query.all()
    form = ProductForm()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    # Check if we're editing a product via GET request with edit_id
    edit_id = request.args.get('edit_id')
    product_to_edit = None
    
    if edit_id:
        product_to_edit = Product.query.get(edit_id)
        if product_to_edit:
            # Pre-populate the form with existing product data
            form.name.data = product_to_edit.name
            form.description.data = product_to_edit.description
            form.category_id.data = product_to_edit.category_id
            form.price.data = product_to_edit.price
            form.discounted_price.data = product_to_edit.discounted_price
    
    if form.validate_on_submit():
        product_id = request.form.get('product_id')
        filename = None
        if form.image.data:
            image = form.image.data
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        if product_id:
            # Update existing product
            product = Product.query.get(product_id)
            product.name = form.name.data
            product.description = form.description.data
            product.category_id = form.category_id.data
            product.price = form.price.data
            product.discounted_price = form.discounted_price.data if form.discounted_price.data else None
            if filename:
                product.image_filename = filename
        else:
            # Add new product
            product = Product(
                name=form.name.data,
                description=form.description.data,
                category_id=form.category_id.data,
                image_filename=filename,
                price=form.price.data,
                discounted_price=form.discounted_price.data if form.discounted_price.data else None
            )
            db.session.add(product)
        db.session.commit()
        flash('Product saved successfully!', 'success')
        return redirect(url_for('admin_products'))
    
    return render_template('admin_products.html', products=products, categories=categories, form=form, product_to_edit=product_to_edit)

@app.route('/admin/categories', methods=['GET', 'POST'])
def admin_categories():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    categories = Category.query.all()
    if request.method == 'POST':
        name = request.form['name']
        slug = name.lower().replace(' ', '-')
        description = request.form.get('description', '')
        category = Category(name=name, slug=slug, description=description)
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('admin_categories'))
    return render_template('admin_categories.html', categories=categories)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)