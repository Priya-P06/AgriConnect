from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import generate_csrf
from werkzeug.utils import secure_filename
from mongoengine import connect, Q
from bson import ObjectId
from bson.errors import InvalidId
import os
import uuid
from datetime import datetime
from decimal import Decimal
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import application modules
from config import Config
from models import User, Product, CartItem, Offer, Order
from forms import (RegistrationForm, LoginForm, ProductForm, EditProductForm, 
                   AddToCartForm, OfferForm, UpdateCartItemForm, SearchForm)

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize MongoDB connection
connect(host=app.config['MONGODB_URI'])

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    try:
        return User.objects(id=ObjectId(user_id)).first()
    except (InvalidId, Exception):
        return None

# Context processor to make CSRF token available in all templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_uploaded_image(image_file):
    """Save uploaded image and return filename"""
    if image_file and allowed_file(image_file.filename):
        # Generate unique filename
        filename = str(uuid.uuid4()) + '.' + image_file.filename.rsplit('.', 1)[1].lower()
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(image_path)
        return filename
    return None

# Database connection check
def check_database_connection():
    """Check if database is available"""
    try:
        # Simple MongoDB connection test
        User.objects().count()
        return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

# Custom pagination class for MongoDB
class Pagination:
    def __init__(self, page, per_page, total, items):
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items
        self.pages = (total - 1) // per_page + 1 if total else 0
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1 if self.has_prev else None
        self.next_num = page + 1 if self.has_next else None

def paginate_query(query, page, per_page):
    """Paginate MongoDB query"""
    total = query.count()
    items = query.skip((page - 1) * per_page).limit(per_page)
    return Pagination(page, per_page, total, items)

# Routes
@app.route('/')
def index():
    """Homepage with featured products"""
    search_form = SearchForm()
    
    # Check database connection
    if not check_database_connection():
        flash('Database is currently unavailable. Please check back later.', 'warning')
        return render_template('index.html', products=None, search_form=search_form, 
                             search_query='', category='')
    
    # Get query parameters for search
    search_query = request.args.get('search_query', '').strip()
    category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    try:
        # Build MongoDB query
        query_filters = Q(is_available=True)
        
        # Apply search filters
        if search_query:
            search_filters = Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(category__icontains=search_query)
            query_filters &= search_filters
        
        if category:
            query_filters &= Q(category=category)
        
        if min_price is not None:
            query_filters &= Q(price__gte=min_price)
        
        if max_price is not None:
            query_filters &= Q(price__lte=max_price)
        
        # Get paginated results
        page = request.args.get('page', 1, type=int)
        query = Product.objects(query_filters).order_by('-created_at')
        products = paginate_query(query, page, 12)
        
        return render_template('index.html', products=products, search_form=search_form, 
                             search_query=search_query, category=category)
    except Exception as e:
        flash('Error loading products. Please try again later.', 'error')
        return render_template('index.html', products=None, search_form=search_form, 
                             search_query=search_query, category=category)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.objects(username=form.username.data).first():
            flash('Username already exists. Please choose a different one.', 'error')
            return render_template('register.html', form=form)
        
        if User.objects(email=form.email.data).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            full_name=form.full_name.data,
            phone=form.phone.data,
            role=form.role.data,
            address=form.address.data
        )
        user.set_password(form.password.data)
        
        try:
            user.save()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('An error occurred during registration. Please try again.', 'error')
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name}!', 'success')
            
            # Redirect based on user role
            if next_page:
                return redirect(next_page)
            elif user.role == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

@app.route('/farmer/dashboard')
@login_required
def farmer_dashboard():
    """Farmer dashboard"""
    if current_user.role != 'farmer':
        flash('Access denied. Farmers only.', 'error')
        return redirect(url_for('index'))
    
    # Get farmer's products
    products = Product.objects(farmer_id=current_user.id).order_by('-created_at').limit(20)
    
    # Get recent offers
    offers = Offer.objects(farmer_id=current_user.id).order_by('-created_at').limit(10)
    
    # Get recent orders
    orders = Order.objects(farmer_id=current_user.id).order_by('-created_at').limit(10)
    
    return render_template('farmer_dashboard.html', products=products, offers=offers, orders=orders)

@app.route('/farmer/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    """Add new product"""
    if current_user.role != 'farmer':
        flash('Access denied. Farmers only.', 'error')
        return redirect(url_for('index'))
    
    form = ProductForm()
    if form.validate_on_submit():
        # Handle image upload
        image_filename = None
        if form.image.data:
            image_filename = save_uploaded_image(form.image.data)
        
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=Decimal(str(form.price.data)),
            quantity=form.quantity.data,
            unit=form.unit.data,
            category=form.category.data,
            image_path=image_filename,
            farmer_id=current_user.id
        )
        
        try:
            product.save()
            flash('Product added successfully!', 'success')
            return redirect(url_for('farmer_dashboard'))
        except Exception as e:
            flash('An error occurred while adding the product.', 'error')
    
    return render_template('add_product.html', form=form)

@app.route('/farmer/edit_product/<product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """Edit existing product"""
    if current_user.role != 'farmer':
        flash('Access denied. Farmers only.', 'error')
        return redirect(url_for('index'))
    
    try:
        product = Product.objects(id=ObjectId(product_id)).first()
    except InvalidId:
        flash('Invalid product ID.', 'error')
        return redirect(url_for('farmer_dashboard'))
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('farmer_dashboard'))
    
    if product.farmer_id != current_user.id:
        flash('Access denied. You can only edit your own products.', 'error')
        return redirect(url_for('farmer_dashboard'))
    
    form = EditProductForm()
    if request.method == 'GET':
        # Populate form with existing data
        form.name.data = product.name
        form.description.data = product.description
        form.price.data = float(product.price)
        form.quantity.data = product.quantity
        form.unit.data = product.unit
        form.category.data = product.category
    
    if form.validate_on_submit():
        # Handle image upload
        if form.image.data:
            image_filename = save_uploaded_image(form.image.data)
            if image_filename:
                # Delete old image if exists
                if product.image_path:
                    old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_path)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                product.image_path = image_filename
        
        # Update product fields
        product.name = form.name.data
        product.description = form.description.data
        product.price = Decimal(str(form.price.data))
        product.quantity = form.quantity.data
        product.unit = form.unit.data
        product.category = form.category.data
        
        try:
            product.save()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('farmer_dashboard'))
        except Exception as e:
            flash('An error occurred while updating the product.', 'error')
    
    return render_template('add_product.html', form=form, product=product, edit_mode=True)

@app.route('/farmer/delete_product/<product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    """Delete product"""
    if current_user.role != 'farmer':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        product = Product.objects(id=ObjectId(product_id)).first()
    except InvalidId:
        return jsonify({'success': False, 'message': 'Invalid product ID'})
    
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    
    if product.farmer_id != current_user.id:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        # Delete image file if exists
        if product.image_path:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        product.delete()
        return jsonify({'success': True, 'message': 'Product deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error deleting product'})

@app.route('/products')
def product_list():
    """List all products"""
    search_form = SearchForm()
    
    # Get query parameters for search
    search_query = request.args.get('search_query', '').strip()
    category = request.args.get('category', '').strip()
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Build MongoDB query
    query_filters = Q(is_available=True)
    
    # Apply search filters
    if search_query:
        search_filters = Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(category__icontains=search_query)
        query_filters &= search_filters
    
    if category:
        query_filters &= Q(category=category)
    
    if min_price is not None:
        query_filters &= Q(price__gte=min_price)
    
    if max_price is not None:
        query_filters &= Q(price__lte=max_price)
    
    # Get paginated results
    page = request.args.get('page', 1, type=int)
    query = Product.objects(query_filters).order_by('-created_at')
    products = paginate_query(query, page, 20)
    
    return render_template('product_list.html', products=products, search_form=search_form)

@app.route('/product/<product_id>')
def product_detail(product_id):
    """Product detail page"""
    try:
        product = Product.objects(id=ObjectId(product_id)).first()
    except InvalidId:
        flash('Invalid product ID.', 'error')
        return redirect(url_for('index'))
    
    if not product:
        flash('Product not found.', 'error')
        return redirect(url_for('index'))
    
    add_to_cart_form = AddToCartForm()
    offer_form = OfferForm()
    
    return render_template('product_detail.html', product=product, 
                         add_to_cart_form=add_to_cart_form, offer_form=offer_form)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    """Add product to cart"""
    if current_user.role != 'consumer':
        return jsonify({'success': False, 'message': 'Only consumers can add items to cart'})
    
    form = AddToCartForm()
    if form.validate_on_submit():
        try:
            product = Product.objects(id=ObjectId(form.product_id.data)).first()
        except InvalidId:
            return jsonify({'success': False, 'message': 'Invalid product ID'})
        
        if not product or not product.is_available:
            return jsonify({'success': False, 'message': 'Product not available'})
        
        if form.quantity.data > product.quantity:
            return jsonify({'success': False, 'message': f'Only {product.quantity} {product.unit} available'})
        
        # Check if item already in cart
        cart_item = CartItem.objects(
            consumer_id=current_user.id,
            product_id=ObjectId(form.product_id.data)
        ).first()
        
        try:
            if cart_item:
                # Update existing cart item
                cart_item.quantity += form.quantity.data
                if cart_item.quantity > product.quantity:
                    cart_item.quantity = product.quantity
                cart_item.save()
            else:
                # Create new cart item
                cart_item = CartItem(
                    consumer_id=current_user.id,
                    product_id=ObjectId(form.product_id.data),
                    quantity=form.quantity.data
                )
                cart_item.save()
            
            # Get cart count
            cart_count = CartItem.objects(consumer_id=current_user.id).count()
            
            return jsonify({
                'success': True, 
                'message': f'{product.name} added to cart',
                'cart_count': cart_count
            })
        except Exception as e:
            return jsonify({'success': False, 'message': 'Error adding to cart'})
    
    return jsonify({'success': False, 'message': 'Invalid form data', 'errors': form.errors})

@app.route('/cart')
@login_required
def consumer_cart():
    """Consumer cart page"""
    if current_user.role != 'consumer':
        flash('Access denied. Consumers only.', 'error')
        return redirect(url_for('index'))
    
    cart_items = CartItem.objects(consumer_id=current_user.id)
    total = sum(item.total_price for item in cart_items)
    
    return render_template('consumer_cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart_item', methods=['POST'])
@login_required
def update_cart_item():
    """Update cart item quantity"""
    if current_user.role != 'consumer':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    data = request.get_json()
    item_id = data.get('item_id')
    quantity = data.get('quantity', 1)
    
    try:
        cart_item = CartItem.objects(id=ObjectId(item_id), consumer_id=current_user.id).first()
    except InvalidId:
        return jsonify({'success': False, 'message': 'Invalid item ID'})
    
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'})
    
    if quantity <= 0:
        # Remove item
        cart_item.delete()
    else:
        if quantity > cart_item.product.quantity:
            return jsonify({'success': False, 'message': f'Only {cart_item.product.quantity} {cart_item.product.unit} available'})
        cart_item.quantity = quantity
        cart_item.save()
    
    return jsonify({'success': True, 'message': 'Cart updated'})

@app.route('/toggle_cart_item_selection', methods=['POST'])
@login_required
def toggle_cart_item_selection():
    """Toggle cart item selection (blue tick)"""
    if current_user.role != 'consumer':
        return jsonify({'success': False, 'message': 'Access denied'})
    
    data = request.get_json()
    item_id = data.get('item_id')
    
    try:
        cart_item = CartItem.objects(id=ObjectId(item_id), consumer_id=current_user.id).first()
    except InvalidId:
        return jsonify({'success': False, 'message': 'Invalid item ID'})
    
    if not cart_item:
        return jsonify({'success': False, 'message': 'Cart item not found'})
    
    cart_item.selected = not cart_item.selected
    cart_item.save()
    
    return jsonify({'success': True, 'selected': cart_item.selected})

@app.route('/send_offer', methods=['POST'])
@login_required
def send_offer():
    """Send price offer to farmer"""
    if current_user.role != 'consumer':
        return jsonify({'success': False, 'message': 'Only consumers can send offers'})
    
    form = OfferForm()
    if form.validate_on_submit():
        try:
            product = Product.objects(id=ObjectId(form.product_id.data)).first()
        except InvalidId:
            return jsonify({'success': False, 'message': 'Invalid product ID'})
        
        if not product or not product.is_available:
            return jsonify({'success': False, 'message': 'Product not available'})
        
        if form.quantity.data > product.quantity:
            return jsonify({'success': False, 'message': f'Only {product.quantity} {product.unit} available'})
        
        offer = Offer(
            consumer_id=current_user.id,
            farmer_id=product.farmer_id,
            product_id=ObjectId(form.product_id.data),
            quantity=form.quantity.data,
            offered_price=Decimal(str(form.offered_price.data)),
            message=form.message.data
        )
        
        try:
            offer.save()
            return jsonify({'success': True, 'message': 'Offer sent successfully'})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Error sending offer'})
    
    return jsonify({'success': False, 'message': 'Invalid form data'})

@app.route('/offers')
@login_required
def offers():
    """View offers (farmer sees received, consumer sees sent)"""
    if current_user.role == 'farmer':
        offers_query = Offer.objects(farmer_id=current_user.id)
    else:
        offers_query = Offer.objects(consumer_id=current_user.id)
    
    page = request.args.get('page', 1, type=int)
    offers_paginated = paginate_query(offers_query.order_by('-created_at'), page, 20)
    
    return render_template('offers.html', offers=offers_paginated)

@app.route('/respond_to_offer/<offer_id>/<action>')
@login_required
def respond_to_offer(offer_id, action):
    """Accept or reject offer"""
    if current_user.role != 'farmer':
        return jsonify({'success': False, 'message': 'Only farmers can respond to offers'})
    
    try:
        offer = Offer.objects(id=ObjectId(offer_id), farmer_id=current_user.id).first()
    except InvalidId:
        return jsonify({'success': False, 'message': 'Invalid offer ID'})
    
    if not offer:
        return jsonify({'success': False, 'message': 'Offer not found'})
    
    if offer.status != 'pending':
        return jsonify({'success': False, 'message': 'Offer already responded to'})
    
    try:
        if action == 'accept':
            offer.accept()
            message = 'Offer accepted and order created'
        elif action == 'reject':
            offer.reject()
            message = 'Offer rejected'
        else:
            return jsonify({'success': False, 'message': 'Invalid action'})
        
        return jsonify({'success': True, 'message': message})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error responding to offer'})

@app.route('/orders')
@login_required
def orders():
    """View orders"""
    if current_user.role == 'farmer':
        orders_query = Order.objects(farmer_id=current_user.id)
    else:
        orders_query = Order.objects(consumer_id=current_user.id)
    
    page = request.args.get('page', 1, type=int)
    orders_paginated = paginate_query(orders_query.order_by('-created_at'), page, 20)
    
    return render_template('orders.html', orders=orders_paginated)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/api/cart_count')
@login_required
def api_cart_count():
    """Get current user's cart item count"""
    if current_user.role != 'consumer':
        return jsonify({'count': 0})
    
    count = CartItem.objects(consumer_id=current_user.id).count()
    return jsonify({'count': count})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Run app
if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("AgriConnect MVP Server Starting (MongoDB)...")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print("Server running at http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
