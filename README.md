# AgriConnect MVP 🌱

A farmer-to-consumer marketplace web application that connects farmers directly with consumers, eliminating middlemen and ensuring fair prices for fresh produce.

## Features ✨

### For Farmers 🚜
- User registration and authentication
- Product management (add, edit, delete products with images)
- Dashboard with sales analytics
- Receive and respond to price offers from consumers
- Order management and tracking

### For Consumers 🛒
- Browse and search products by category, price, etc.
- Add products to cart with blue tick selection feature
- Send price offers to farmers (negotiate)
- View and track orders
- Responsive design for mobile and desktop

### Key Functionality
- **Direct Trading**: Farmers and consumers can negotiate prices directly
- **Product Selection**: Blue tick system for selecting cart items
- **Image Upload**: Product images with secure file handling
- **Real-time Updates**: AJAX-powered interactions
- **Responsive UI**: Bootstrap-based responsive design

## Tech Stack 🛠️

- **Backend**: Python Flask
- **Database**: MongoDB with MongoEngine ODM
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Icons**: Font Awesome 6
- **Authentication**: Flask-Login
- **Forms**: Flask-WTF with WTForms
- **File Uploads**: Werkzeug secure file handling
- **Deployment**: Vercel (Serverless) + MongoDB Atlas

## Installation & Setup 🚀

### 🌍 Option 1: Deploy on Vercel + MongoDB Atlas (Recommended)

**For a complete production deployment, see our detailed [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)**

### 💻 Option 2: Local Development Setup

#### Prerequisites
- Python 3.8+
- MongoDB (local installation or MongoDB Atlas account)
- Git

#### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd agri_connect_mvp
```

#### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Database Setup

**Option A: Local MongoDB**
1. Install MongoDB locally from [https://mongodb.com/try/download/community](https://mongodb.com/try/download/community)
2. Start MongoDB service
3. The app will connect to `mongodb://localhost:27017/agri_connect_db` by default

**Option B: MongoDB Atlas (Cloud)**
1. Create account at [https://cloud.mongodb.com](https://cloud.mongodb.com)
2. Create a free cluster (M0)
3. Get your connection string
4. Create a `.env` file:
   ```
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/agri_connect_db?retryWrites=true&w=majority
   SECRET_KEY=your-secret-key-here
   ```

#### 5. Initialize Database and Seed Data
```bash
python seed_db.py
```

#### 6. Run the Application
```bash
python app.py
```

The application will be available at: **http://localhost:5000**

## Demo Credentials 👥

### Farmers
- **Username**: `farmer_john` | **Password**: `farmer123`
- **Username**: `farmer_mary` | **Password**: `farmer123`
- **Username**: `farmer_david` | **Password**: `farmer123`

### Consumers
- **Username**: `consumer_alice` | **Password**: `consumer123`
- **Username**: `consumer_bob` | **Password**: `consumer123`
- **Username**: `retailer_sam` | **Password**: `retailer123`

## Project Structure 📁

```
agri_connect_mvp/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── forms.py               # WTForms for user input
├── config.py              # Configuration settings
├── seed_db.py             # Database seeding script
├── create_tables.sql      # SQL database schema
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── static/
│   ├── css/
│   │   └── styles.css     # Custom CSS styles
│   ├── js/
│   │   └── main.js        # JavaScript functionality
│   └── uploads/           # Product images
└── templates/             # HTML templates
    ├── base.html          # Base template
    ├── index.html         # Homepage
    ├── login.html         # Login page
    ├── register.html      # Registration page
    ├── farmer_dashboard.html    # Farmer dashboard
    ├── add_product.html   # Add/Edit product form
    ├── product_list.html  # Product listing
    ├── product_detail.html # Product details (to be created)
    ├── consumer_cart.html # Shopping cart
    ├── offers.html        # Offers page (to be created)
    └── orders.html        # Orders page (to be created)
```

## Key Features Explained 🔍

### Blue Tick Selection System
- Consumers can select items in their cart using blue tick icons
- Selected items can be negotiated as a group
- Visual feedback with animations and color changes

### Price Negotiation
- Consumers send offers to farmers with custom prices
- Farmers can accept/reject offers
- Accepted offers automatically create orders

### Image Upload
- Secure file upload for product images
- Automatic filename generation with UUIDs
- Image validation and size limits

### Responsive Design
- Mobile-first approach with Bootstrap 5
- Works seamlessly on desktop, tablet, and mobile
- Touch-friendly interface elements

## API Endpoints 🔌

### Authentication
- `GET/POST /login` - User login
- `GET/POST /register` - User registration
- `GET /logout` - User logout

### Products
- `GET /products` - List all products
- `GET /product/<id>` - Product details
- `POST /add_to_cart` - Add product to cart

### Cart & Orders
- `GET /cart` - View cart
- `POST /update_cart_item` - Update cart item
- `POST /toggle_cart_item_selection` - Toggle item selection

### Offers & Negotiations
- `POST /send_offer` - Send price offer
- `GET /offers` - View offers
- `GET /respond_to_offer/<id>/<action>` - Accept/reject offer

## Troubleshooting 🔧

### Common Issues

1. **MongoDB Connection Error**
   - Check if MongoDB service is running (local installation)
   - Verify `MONGODB_URI` in your environment variables
   - For Atlas: ensure IP whitelist includes 0.0.0.0/0 for development
   - Test connection string in MongoDB Compass

2. **Module Not Found**
   - Make sure virtual environment is activated
   - Run `pip install -r requirements.txt`
   - Check if all MongoDB dependencies are installed

3. **File Upload Issues**
   - Check `static/uploads/` directory exists
   - Verify file permissions
   - Ensure `UPLOAD_FOLDER` is properly configured

4. **Port Already in Use**
   - Change port in `app.py`: `app.run(port=5001)`

5. **Vercel Deployment Issues**
   - Check environment variables are set in Vercel dashboard
   - Verify `MONGODB_URI` format for Atlas
   - Check deployment logs in Vercel Functions tab

## Future Enhancements 🚀

- [ ] Payment integration (Stripe/PayPal)
- [ ] Real-time messaging between farmers and consumers
- [ ] Advanced search with filters
- [ ] Delivery tracking system
- [ ] Review and rating system
- [ ] Mobile app (React Native/Flutter)
- [ ] Email notifications
- [ ] Admin panel for platform management

## Contributing 🤝

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License 📝

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact 📧

Project Link: [https://agriconnect-neon.vercel.app/](https://agriconnect-neon.vercel.app/)

---

**Built with ❤️ for farmers and consumers**





