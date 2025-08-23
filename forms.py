from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length, NumberRange, EqualTo, ValidationError, Optional
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message="Username must be between 3 and 20 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Please enter a valid email address")
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=100, message="Full name must be between 2 and 100 characters")
    ])
    phone = StringField('Phone Number', validators=[
        Optional(),
        Length(max=20, message="Phone number cannot exceed 20 characters")
    ])
    role = SelectField('I am a', choices=[
        ('farmer', 'Farmer - I want to sell my produce'),
        ('consumer', 'Consumer - I want to buy produce')
    ], validators=[DataRequired()])
    address = TextAreaField('Address', validators=[
        Optional(),
        Length(max=500, message="Address cannot exceed 500 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Password must be at least 6 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different email address.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[
        DataRequired(),
        Length(min=2, max=200, message="Product name must be between 2 and 200 characters")
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000, message="Description cannot exceed 1000 characters")
    ])
    price = DecimalField('Price per Unit (₹)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message="Price must be greater than 0")
    ], places=2)
    quantity = IntegerField('Available Quantity', validators=[
        DataRequired(),
        NumberRange(min=1, message="Quantity must be at least 1")
    ])
    unit = SelectField('Unit', choices=[
        ('kg', 'Kilograms (kg)'),
        ('tons', 'Tons'),
        ('pieces', 'Pieces'),
        ('liters', 'Liters'),
        ('boxes', 'Boxes'),
        ('bags', 'Bags')
    ], validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('', 'Select a category'),
        ('Vegetables', 'Vegetables'),
        ('Fruits', 'Fruits'),
        ('Grains', 'Grains & Cereals'),
        ('Dairy & Eggs', 'Dairy & Eggs'),
        ('Meat & Poultry', 'Meat & Poultry'),
        ('Herbs', 'Herbs & Spices'),
        ('Natural Products', 'Natural Products'),
        ('Others', 'Others')
    ], validators=[DataRequired()])
    image = FileField('Product Image', validators=[
        FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Save Product')

class EditProductForm(ProductForm):
    submit = SubmitField('Update Product')

class AddToCartForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
        DataRequired(),
        NumberRange(min=1, message="Quantity must be at least 1")
    ], default=1)
    submit = SubmitField('Add to Cart')

class OfferForm(FlaskForm):
    product_id = HiddenField('Product ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
        DataRequired(),
        NumberRange(min=1, message="Quantity must be at least 1")
    ])
    offered_price = DecimalField('Your Offered Price per Unit (₹)', validators=[
        DataRequired(),
        NumberRange(min=0.01, message="Price must be greater than 0")
    ], places=2)
    message = TextAreaField('Message to Farmer (Optional)', validators=[
        Optional(),
        Length(max=500, message="Message cannot exceed 500 characters")
    ])
    submit = SubmitField('Send Offer')

class UpdateCartItemForm(FlaskForm):
    item_id = HiddenField('Item ID', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[
        DataRequired(),
        NumberRange(min=1, message="Quantity must be at least 1")
    ])
    submit = SubmitField('Update')

class SearchForm(FlaskForm):
    search_query = StringField('Search Products', validators=[
        Optional(),
        Length(max=100, message="Search query cannot exceed 100 characters")
    ])
    category = SelectField('Category', choices=[
        ('', 'All Categories'),
        ('Vegetables', 'Vegetables'),
        ('Fruits', 'Fruits'),
        ('Grains', 'Grains & Cereals'),
        ('Dairy & Eggs', 'Dairy & Eggs'),
        ('Meat & Poultry', 'Meat & Poultry'),
        ('Herbs', 'Herbs & Spices'),
        ('Natural Products', 'Natural Products'),
        ('Others', 'Others')
    ])
    min_price = DecimalField('Min Price', validators=[
        Optional(),
        NumberRange(min=0, message="Price must be non-negative")
    ], places=2)
    max_price = DecimalField('Max Price', validators=[
        Optional(),
        NumberRange(min=0, message="Price must be non-negative")
    ], places=2)
    submit = SubmitField('Search')
    
    def validate(self):
        if not FlaskForm.validate(self):
            return False
        
        if self.min_price.data and self.max_price.data:
            if self.min_price.data > self.max_price.data:
                self.max_price.errors.append('Maximum price must be greater than minimum price')
                return False
        
        return True
