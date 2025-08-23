# 🚀 AgriConnect MVP Deployment Guide

This guide will help you deploy your AgriConnect application using **MongoDB Atlas** (cloud database) and **Vercel** (serverless hosting).

## 📋 Prerequisites

- GitHub account
- Vercel account (sign up at [vercel.com](https://vercel.com))
- MongoDB Atlas account (sign up at [cloud.mongodb.com](https://cloud.mongodb.com))

## 🗃️ Part 1: MongoDB Atlas Setup

### Step 1: Create MongoDB Atlas Account
1. Go to [https://cloud.mongodb.com](https://cloud.mongodb.com)
2. Click "Sign up" and create your free account
3. Verify your email address

### Step 2: Create a New Cluster
1. After logging in, click "Create a New Cluster"
2. Choose **"Shared Clusters"** (Free tier)
3. Select **"M0 Sandbox"** (512MB storage - free forever)
4. Choose your preferred cloud provider and region
5. Give your cluster a name (e.g., `agriconnect-cluster`)
6. Click **"Create Cluster"** (takes 1-3 minutes)

### Step 3: Create Database User
1. In the left sidebar, click **"Database Access"**
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication method
4. Enter username: `agri_user` (or your preferred username)
5. Generate a secure password or create your own
6. Set **"Read and write to any database"** permissions
7. Click **"Add User"**
8. **⚠️ Important**: Save these credentials safely!

### Step 4: Configure Network Access
1. In the left sidebar, click **"Network Access"**
2. Click **"Add IP Address"**
3. For development, click **"Allow Access From Anywhere"** (0.0.0.0/0)
   - For production, restrict to specific IPs
4. Click **"Confirm"**

### Step 5: Get Connection String
1. Go back to **"Clusters"** in the left sidebar
2. Click **"Connect"** button on your cluster
3. Select **"Connect your application"**
4. Choose **Python** and version **3.6 or later**
5. Copy the connection string - it looks like:
   ```
   mongodb+srv://agri_user:<password>@agriconnect-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. Replace `<password>` with your actual password
7. Add the database name before the `?` like this:
   ```
   mongodb+srv://agri_user:yourpassword@agriconnect-cluster.xxxxx.mongodb.net/agri_connect_db?retryWrites=true&w=majority
   ```

## 🌐 Part 2: Vercel Deployment

### Step 1: Prepare Your Code
1. Make sure all files are committed to your GitHub repository
2. Ensure your `vercel.json` file is in the project root:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "vercel_app.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "vercel_app.py"
       }
     ],
     "env": {
       "PYTHONPATH": "./"
     }
   }
   ```

### Step 2: Deploy to Vercel
1. Go to [vercel.com](https://vercel.com) and sign in
2. Click **"New Project"**
3. Connect your GitHub account if not already connected
4. Select your `agri_connect_mvp` repository
5. Click **"Import"**
6. Vercel will detect it's a Python project automatically
7. Click **"Deploy"**

### Step 3: Add Environment Variables
1. After deployment, go to your project dashboard in Vercel
2. Click **"Settings"** tab
3. Click **"Environment Variables"** in the left sidebar
4. Add the following variables:

   **MONGODB_URI** (Required):
   ```
   mongodb+srv://agri_user:yourpassword@agriconnect-cluster.xxxxx.mongodb.net/agri_connect_db?retryWrites=true&w=majority
   ```
   
   **SECRET_KEY** (Required):
   ```
   your-super-secret-key-change-this-in-production-make-it-long-and-random
   ```

5. Click **"Add"** for each environment variable
6. Make sure to select **"Production"**, **"Preview"**, and **"Development"** for each variable

### Step 4: Redeploy
1. After adding environment variables, go to the **"Deployments"** tab
2. Click the **"..."** menu on the latest deployment
3. Click **"Redeploy"**
4. Wait for the new deployment to complete

## 🎯 Part 3: Seed Your Database

### Option 1: Using the Web Interface (Recommended)
1. Once your app is deployed, visit your Vercel URL
2. Register as a farmer and consumer to test the functionality
3. Add some products to see the app in action

### Option 2: Run Seed Script Locally
1. In your local project directory, create a `.env` file:
   ```
   MONGODB_URI=mongodb+srv://agri_user:yourpassword@agriconnect-cluster.xxxxx.mongodb.net/agri_connect_db?retryWrites=true&w=majority
   SECRET_KEY=your-secret-key
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the seed script:
   ```bash
   python seed_db.py
   ```

4. This will create sample users and products with these credentials:
   **Farmers:**
   - Username: `farmer_john`, Password: `farmer123`
   - Username: `farmer_mary`, Password: `farmer123`
   - Username: `farmer_david`, Password: `farmer123`

   **Consumers:**
   - Username: `consumer_alice`, Password: `consumer123`
   - Username: `consumer_bob`, Password: `consumer123`
   - Username: `retailer_sam`, Password: `retailer123`

## 🔧 Part 4: Verify Deployment

### Test Your Application
1. Visit your Vercel URL (found in your Vercel dashboard)
2. You should see the AgriConnect homepage
3. Try registering a new account
4. Test login functionality
5. For farmers: try adding products
6. For consumers: try browsing and adding items to cart

### Check Database Connection
- Visit `your-app-url.vercel.app/health` to check if the database is connected properly

## 🐛 Troubleshooting

### Common Issues:

1. **"MongoDB not configured" error**:
   - Double-check your `MONGODB_URI` environment variable
   - Ensure the password in the connection string is correct
   - Verify your MongoDB Atlas IP whitelist includes 0.0.0.0/0

2. **"Database connection failed"**:
   - Check if your MongoDB Atlas cluster is running
   - Verify the database user has proper permissions
   - Test the connection string in MongoDB Compass or another client

3. **Application deployment fails**:
   - Check Vercel deployment logs in the Functions tab
   - Ensure all required dependencies are in `requirements.txt`
   - Verify `vercel.json` configuration is correct

4. **Static files not loading**:
   - Ensure all CSS/JS files are committed to your repository
   - Check if file paths are correct in your templates

### Getting Help
- MongoDB Atlas docs: [https://docs.atlas.mongodb.com/](https://docs.atlas.mongodb.com/)
- Vercel docs: [https://vercel.com/docs](https://vercel.com/docs)
- Flask docs: [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)

## 🎉 Congratulations!

Your AgriConnect MVP is now live! 🌱

Your application features:
- ✅ User authentication for farmers and consumers
- ✅ Product listing and management
- ✅ Shopping cart functionality
- ✅ Offer system for price negotiation
- ✅ Order management
- ✅ Responsive design
- ✅ Cloud database with MongoDB Atlas
- ✅ Serverless hosting with Vercel

## 📈 Next Steps for Production

1. **Security Enhancements**:
   - Generate a strong, unique `SECRET_KEY`
   - Implement rate limiting
   - Add HTTPS enforcement
   - Set up proper IP whitelisting for MongoDB

2. **Performance Optimization**:
   - Enable MongoDB Atlas connection pooling
   - Implement caching for frequently accessed data
   - Optimize database queries with indexes

3. **Monitoring & Analytics**:
   - Set up error tracking (e.g., Sentry)
   - Monitor database performance in MongoDB Atlas
   - Use Vercel Analytics for usage insights

4. **Additional Features**:
   - Email notifications for orders
   - Payment integration
   - Advanced search and filtering
   - Mobile app development

---

**Happy farming! 🚜🌾**
