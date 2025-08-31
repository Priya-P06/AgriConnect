# Vercel entry point for AgriConnect MVP
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set required environment variables if not already set
if not os.environ.get('MONGODB_URI'):
    os.environ['MONGODB_URI'] = 'mongodb+srv://priyapremnmkl5:mlBObqUYLnQK0WUf@agriconnect.2clc19t.mongodb.net/agri_connect_db?retryWrites=true&w=majority&appName=AgriConnect'
if not os.environ.get('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'KgxxSH0ChsvTxm4qVM6XCAi6JPenycLWPIEBfNrg8mI'

# Import the main application
from app import app

# Export for Vercel
application = app

if __name__ == '__main__':
    app.run(debug=True)
