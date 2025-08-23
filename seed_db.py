import os
from mongoengine import connect
from decimal import Decimal
from models import User, Product
from config import Config

def seed_database():
    """Populate MongoDB database with sample data"""
    
    # Connect to MongoDB
    connect(host=Config.MONGODB_URI)
    
    # Check if data already exists
    if User.objects().first():
        print("Database already has data. Skipping seeding.")
        return
    
    # Create sample farmers
    farmers = [
        {
            'username': 'farmer_john',
            'email': 'john@farmer.com',
            'password': 'farmer123',
            'full_name': 'John Smith',
            'phone': '+1234567890',
            'role': 'farmer',
            'address': '123 Farm Road, Agricultural Valley, State 12345'
        },
        {
            'username': 'farmer_mary',
            'email': 'mary@farmer.com',
            'password': 'farmer123',
            'full_name': 'Mary Johnson',
            'phone': '+1234567891',
            'role': 'farmer',
            'address': '456 Green Acres, Farm Town, State 12346'
        },
        {
            'username': 'farmer_david',
            'email': 'david@farmer.com',
            'password': 'farmer123',
            'full_name': 'David Wilson',
            'phone': '+1234567892',
            'role': 'farmer',
            'address': '789 Organic Farm Lane, Nature Valley, State 12347'
        }
    ]
    
    # Create sample consumers
    consumers = [
        {
            'username': 'consumer_alice',
            'email': 'alice@consumer.com',
            'password': 'consumer123',
            'full_name': 'Alice Brown',
            'phone': '+1234567893',
            'role': 'consumer',
            'address': '321 City Street, Urban Area, State 54321'
        },
        {
            'username': 'consumer_bob',
            'email': 'bob@consumer.com',
            'password': 'consumer123',
            'full_name': 'Bob Davis',
            'phone': '+1234567894',
            'role': 'consumer',
            'address': '654 Market Avenue, Downtown, State 54322'
        },
        {
            'username': 'retailer_sam',
            'email': 'sam@retailer.com',
            'password': 'retailer123',
            'full_name': 'Sam Wilson (Fresh Mart)',
            'phone': '+1234567895',
            'role': 'consumer',
            'address': '987 Business District, Commercial Area, State 54323'
        }
    ]
    
    # Add users to database
    user_objects = []
    for user_data in farmers + consumers:
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            full_name=user_data['full_name'],
            phone=user_data['phone'],
            role=user_data['role'],
            address=user_data['address']
        )
        user.set_password(user_data['password'])
        user.save()
        user_objects.append(user)
    
    print("Sample users created successfully!")
    
    # Get farmer objects
    farmer1 = User.objects(username='farmer_john').first()
    farmer2 = User.objects(username='farmer_mary').first()
    farmer3 = User.objects(username='farmer_david').first()
    
    # Create sample products
    products = [
        # John's products
        {
            'name': 'Fresh Tomatoes',
            'description': 'Organic vine-ripened tomatoes, perfect for salads and cooking. Grown without pesticides.',
            'price': Decimal('3.50'),
            'quantity': 500,
            'unit': 'kg',
            'category': 'Vegetables',
            'farmer_id': farmer1.id,
            'image_path': 'tomatoes.jpg'
        },
        {
            'name': 'Sweet Corn',
            'description': 'Fresh sweet corn harvested daily. Great for grilling or boiling.',
            'price': Decimal('2.75'),
            'quantity': 300,
            'unit': 'kg',
            'category': 'Vegetables',
            'farmer_id': farmer1.id,
            'image_path': 'corn.jpg'
        },
        {
            'name': 'Farm Fresh Eggs',
            'description': 'Free-range chicken eggs from happy hens. Rich in protein and omega-3.',
            'price': Decimal('0.50'),
            'quantity': 1000,
            'unit': 'pieces',
            'category': 'Dairy & Eggs',
            'farmer_id': farmer1.id,
            'image_path': 'eggs.jpg'
        },
        
        # Mary's products
        {
            'name': 'Organic Apples',
            'description': 'Crisp and sweet organic apples, perfect for snacking or baking.',
            'price': Decimal('4.25'),
            'quantity': 200,
            'unit': 'kg',
            'category': 'Fruits',
            'farmer_id': farmer2.id,
            'image_path': 'apples.jpg'
        },
        {
            'name': 'Fresh Strawberries',
            'description': 'Juicy red strawberries, hand-picked at peak ripeness.',
            'price': Decimal('8.50'),
            'quantity': 150,
            'unit': 'kg',
            'category': 'Fruits',
            'farmer_id': farmer2.id,
            'image_path': 'strawberries.jpg'
        },
        {
            'name': 'Mixed Salad Greens',
            'description': 'Fresh mix of lettuce, spinach, and arugula. Washed and ready to eat.',
            'price': Decimal('6.00'),
            'quantity': 100,
            'unit': 'kg',
            'category': 'Vegetables',
            'farmer_id': farmer2.id,
            'image_path': 'salad_greens.jpg'
        },
        
        # David's products
        {
            'name': 'Organic Carrots',
            'description': 'Sweet and crunchy organic carrots, great for cooking or snacking.',
            'price': Decimal('2.25'),
            'quantity': 400,
            'unit': 'kg',
            'category': 'Vegetables',
            'farmer_id': farmer3.id,
            'image_path': 'carrots.jpg'
        },
        {
            'name': 'Fresh Potatoes',
            'description': 'Versatile potatoes perfect for mashing, frying, or roasting.',
            'price': Decimal('1.75'),
            'quantity': 800,
            'unit': 'kg',
            'category': 'Vegetables',
            'farmer_id': farmer3.id,
            'image_path': 'potatoes.jpg'
        },
        {
            'name': 'Organic Honey',
            'description': 'Pure wildflower honey from our beehives. No additives or processing.',
            'price': Decimal('12.00'),
            'quantity': 50,
            'unit': 'kg',
            'category': 'Natural Products',
            'farmer_id': farmer3.id,
            'image_path': 'honey.jpg'
        },
        {
            'name': 'Fresh Herbs Mix',
            'description': 'Mixed fresh herbs including basil, parsley, cilantro, and mint.',
            'price': Decimal('15.00'),
            'quantity': 25,
            'unit': 'kg',
            'category': 'Herbs',
            'farmer_id': farmer3.id,
            'image_path': 'herbs.jpg'
        }
    ]
    
    # Add products to database
    for product_data in products:
        product = Product(**product_data)
        product.save()
    
    print("Sample products created successfully!")
    
    print("\n=== SAMPLE LOGIN CREDENTIALS ===")
    print("FARMERS:")
    print("- Username: farmer_john, Password: farmer123")
    print("- Username: farmer_mary, Password: farmer123")
    print("- Username: farmer_david, Password: farmer123")
    print("\nCONSUMERS:")
    print("- Username: consumer_alice, Password: consumer123")
    print("- Username: consumer_bob, Password: consumer123")
    print("- Username: retailer_sam, Password: retailer123")
    print("\nMongoDB database seeded successfully!")

if __name__ == '__main__':
    seed_database()
