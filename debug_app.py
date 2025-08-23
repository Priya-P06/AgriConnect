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
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
try:
    connect(host=app.config['MONGODB_URI'])
    logger.info("MongoDB connection successful")
except Exception as e:
    logger.error(f"MongoDB connection failed: {e}")

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
    except (InvalidId, Exception) as e:
        logger.error(f"Error loading user {user_id}: {e}")
        return None

# Context processor to make CSRF token available in all templates
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    logger.info("Register route accessed")
    
    if current_user.is_authenticated:
        logger.info("User already authenticated, redirecting to index")
        return redirect(url_for('index'))
    
    try:
        form = RegistrationForm()
        logger.info(f"Registration form created: {form}")
        
        if form.validate_on_submit():
            logger.info("Form validation passed")
            
            # Check if username or email already exists
            try:
                existing_user = User.objects(username=form.username.data).first()
                if existing_user:
                    logger.warning(f"Username {form.username.data} already exists")
                    flash('Username already exists. Please choose a different one.', 'error')
                    return render_template('register.html', form=form)
                
                existing_email = User.objects(email=form.email.data).first()
                if existing_email:
                    logger.warning(f"Email {form.email.data} already exists")
                    flash('Email already registered. Please use a different email.', 'error')
                    return render_template('register.html', form=form)
                
                # Create new user
                user = User(
                    username=form.username.data,
                    email=form.email.data,
                    full_name=form.full_name.data,
                    phone=form.phone.data,
                    role=form.role.data,
                    address=form.address.data
                )
                user.set_password(form.password.data)
                
                logger.info(f"Created user object: {user.username}")
                
                # Save to database
                user.save()
                logger.info(f"User {user.username} saved successfully")
                
                flash('Registration successful! You can now log in.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                logger.error(f"Database error during registration: {e}")
                logger.error(traceback.format_exc())
                flash('An error occurred during registration. Please try again.', 'error')
        else:
            logger.warning(f"Form validation failed: {form.errors}")
        
        return render_template('register.html', form=form)
        
    except Exception as e:
        logger.error(f"Unexpected error in register route: {e}")
        logger.error(traceback.format_exc())
        flash('An unexpected error occurred. Please try again.', 'error')
        return render_template('500.html'), 500

@app.route('/login', methods=['GET', 'POST'])  
def login():
    """User login"""
    logger.info("Login route accessed")
    
    if current_user.is_authenticated:
        logger.info("User already authenticated, redirecting to index")
        return redirect(url_for('index'))
    
    try:
        form = LoginForm()
        logger.info(f"Login form created: {form}")
        
        if form.validate_on_submit():
            logger.info(f"Form validation passed for username: {form.username.data}")
            
            try:
                user = User.objects(username=form.username.data).first()
                logger.info(f"User query result: {user}")
                
                if user and user.check_password(form.password.data):
                    logger.info(f"Password verified for user: {user.username}")
                    
                    login_user(user, remember=True)
                    logger.info(f"User {user.username} logged in successfully")
                    
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
                    logger.warning(f"Invalid login attempt for username: {form.username.data}")
                    flash('Invalid username or password.', 'error')
                    
            except Exception as e:
                logger.error(f"Database error during login: {e}")
                logger.error(traceback.format_exc())
                flash('An error occurred during login. Please try again.', 'error')
        else:
            logger.warning(f"Form validation failed: {form.errors}")
    
        return render_template('login.html', form=form)
        
    except Exception as e:
        logger.error(f"Unexpected error in login route: {e}")
        logger.error(traceback.format_exc())
        flash('An unexpected error occurred. Please try again.', 'error')
        return render_template('500.html'), 500

@app.route('/')
def index():
    """Homepage with featured products"""
    logger.info("Index route accessed")
    try:
        # Simple version for debugging
        return render_template('index.html', products=None, search_form=None, 
                             search_query='', category='')
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        logger.error(traceback.format_exc())
        return render_template('500.html'), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 error: {error}")
    return render_template('500.html'), 500

# Run app
if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    print("AgriConnect DEBUG Server Starting (MongoDB)...")
    print(f"Upload folder: {app.config['UPLOAD_FOLDER']}")
    print("Server running at http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
