from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from mongoengine import Document, fields, connect
from bson import ObjectId
from decimal import Decimal

class User(UserMixin, Document):
    """User document for MongoDB"""
    meta = {
        'collection': 'users',
        'indexes': [
            {'fields': ['username'], 'unique': True},
            {'fields': ['email'], 'unique': True}
        ]
    }
    
    username = fields.StringField(max_length=80, required=True, unique=True)
    email = fields.EmailField(required=True, unique=True)
    password_hash = fields.StringField(max_length=255, required=True)
    full_name = fields.StringField(max_length=200, required=True)
    phone = fields.StringField(max_length=20)
    role = fields.StringField(max_length=20, choices=['farmer', 'consumer'], required=True)
    address = fields.StringField()
    created_at = fields.DateTimeField(default=datetime.utcnow)
    is_active = fields.BooleanField(default=True)
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Return the user ID as string for Flask-Login"""
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Product(Document):
    """Product document for MongoDB"""
    meta = {
        'collection': 'products',
        'indexes': [
            'farmer_id',
            'category',
            'is_available',
            'created_at'
        ]
    }
    
    name = fields.StringField(max_length=200, required=True)
    description = fields.StringField()
    price = fields.DecimalField(min_value=0, precision=2, required=True)
    quantity = fields.IntField(min_value=0, required=True)
    unit = fields.StringField(max_length=20, default='kg')
    image_path = fields.StringField(max_length=255)
    category = fields.StringField(max_length=100)
    farmer_id = fields.ObjectIdField(required=True)
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    is_available = fields.BooleanField(default=True)
    
    @property
    def farmer(self):
        """Get farmer user object"""
        return User.objects(id=self.farmer_id).first()
    
    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super(Product, self).save(*args, **kwargs)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class CartItem(Document):
    """Cart item document for MongoDB"""
    meta = {
        'collection': 'cart_items',
        'indexes': [
            'consumer_id',
            'product_id',
            ('consumer_id', 'product_id')
        ]
    }
    
    consumer_id = fields.ObjectIdField(required=True)
    product_id = fields.ObjectIdField(required=True)
    quantity = fields.IntField(min_value=1, required=True)
    selected = fields.BooleanField(default=False)
    added_at = fields.DateTimeField(default=datetime.utcnow)
    
    @property
    def consumer(self):
        """Get consumer user object"""
        return User.objects(id=self.consumer_id).first()
    
    @property
    def product(self):
        """Get product object"""
        return Product.objects(id=self.product_id).first()
    
    @property
    def total_price(self):
        """Calculate total price"""
        product = self.product
        if product:
            return float(product.price) * self.quantity
        return 0
    
    def __repr__(self):
        consumer = self.consumer
        product = self.product
        consumer_name = consumer.username if consumer else "Unknown"
        product_name = product.name if product else "Unknown"
        return f'<CartItem {consumer_name} - {product_name}>'

class Offer(Document):
    """Offer document for MongoDB"""
    meta = {
        'collection': 'offers',
        'indexes': [
            'consumer_id',
            'farmer_id',
            'product_id',
            'status',
            'created_at'
        ]
    }
    
    consumer_id = fields.ObjectIdField(required=True)
    farmer_id = fields.ObjectIdField(required=True)
    product_id = fields.ObjectIdField(required=True)
    quantity = fields.IntField(min_value=1, required=True)
    offered_price = fields.DecimalField(min_value=0, precision=2, required=True)
    message = fields.StringField()
    status = fields.StringField(max_length=20, choices=['pending', 'accepted', 'rejected'], default='pending')
    created_at = fields.DateTimeField(default=datetime.utcnow)
    responded_at = fields.DateTimeField()
    
    @property
    def consumer(self):
        """Get consumer user object"""
        return User.objects(id=self.consumer_id).first()
    
    @property
    def farmer(self):
        """Get farmer user object"""
        return User.objects(id=self.farmer_id).first()
    
    @property
    def product(self):
        """Get product object"""
        return Product.objects(id=self.product_id).first()
    
    @property
    def total_amount(self):
        """Calculate total amount"""
        return float(self.offered_price) * self.quantity
    
    def accept(self):
        """Accept offer and create order"""
        self.status = 'accepted'
        self.responded_at = datetime.utcnow()
        self.save()
        
        # Create an order when offer is accepted
        order = Order(
            consumer_id=self.consumer_id,
            farmer_id=self.farmer_id,
            product_id=self.product_id,
            quantity=self.quantity,
            price_per_unit=self.offered_price,
            total_amount=Decimal(str(self.total_amount)),
            offer_id=self.id
        )
        order.save()
        return order
    
    def reject(self):
        """Reject offer"""
        self.status = 'rejected'
        self.responded_at = datetime.utcnow()
        self.save()
    
    def __repr__(self):
        consumer = self.consumer
        farmer = self.farmer
        consumer_name = consumer.username if consumer else "Unknown"
        farmer_name = farmer.username if farmer else "Unknown"
        return f'<Offer {consumer_name} to {farmer_name}>'

class Order(Document):
    """Order document for MongoDB"""
    meta = {
        'collection': 'orders',
        'indexes': [
            'consumer_id',
            'farmer_id',
            'product_id',
            'status',
            'created_at'
        ]
    }
    
    consumer_id = fields.ObjectIdField(required=True)
    farmer_id = fields.ObjectIdField(required=True)
    product_id = fields.ObjectIdField(required=True)
    quantity = fields.IntField(min_value=1, required=True)
    price_per_unit = fields.DecimalField(min_value=0, precision=2, required=True)
    total_amount = fields.DecimalField(min_value=0, precision=2, required=True)
    status = fields.StringField(
        max_length=20, 
        choices=['pending', 'confirmed', 'in_transit', 'delivered', 'cancelled'], 
        default='pending'
    )
    offer_id = fields.ObjectIdField()
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    delivery_address = fields.StringField()
    notes = fields.StringField()
    
    @property
    def consumer(self):
        """Get consumer user object"""
        return User.objects(id=self.consumer_id).first()
    
    @property
    def farmer(self):
        """Get farmer user object"""
        return User.objects(id=self.farmer_id).first()
    
    @property
    def product(self):
        """Get product object"""
        return Product.objects(id=self.product_id).first()
    
    @property
    def offer(self):
        """Get offer object if exists"""
        if self.offer_id:
            return Offer.objects(id=self.offer_id).first()
        return None
    
    def save(self, *args, **kwargs):
        """Override save to update timestamp"""
        self.updated_at = datetime.utcnow()
        return super(Order, self).save(*args, **kwargs)
    
    def __repr__(self):
        consumer = self.consumer
        consumer_name = consumer.username if consumer else "Unknown"
        return f'<Order {self.id} - {consumer_name}>'
