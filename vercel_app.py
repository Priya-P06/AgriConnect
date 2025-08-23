# Vercel entry point - Diagnostic version
import os
import sys
import traceback
from flask import Flask, jsonify, render_template_string

# Create a simple diagnostic Flask app
app = Flask(__name__)

@app.route('/')
def index():
    try:
        # Check Python version
        python_version = sys.version
        
        # Check environment variables
        mongodb_uri = os.environ.get('MONGODB_URI', 'NOT SET')
        secret_key = os.environ.get('SECRET_KEY', 'NOT SET')
        
        # Check if we can import required modules
        import_status = {}
        try:
            import flask
            import_status['flask'] = f'✅ {flask.__version__}'
        except Exception as e:
            import_status['flask'] = f'❌ {str(e)}'
            
        try:
            import mongoengine
            import_status['mongoengine'] = f'✅ {mongoengine.__version__}'
        except Exception as e:
            import_status['mongoengine'] = f'❌ {str(e)}'
            
        try:
            import pymongo
            import_status['pymongo'] = f'✅ {pymongo.__version__}'
        except Exception as e:
            import_status['pymongo'] = f'❌ {str(e)}'
            
        try:
            from dotenv import load_dotenv
            import_status['python-dotenv'] = '✅ Available'
        except Exception as e:
            import_status['python-dotenv'] = f'❌ {str(e)}'
        
        # Test MongoDB connection
        db_status = 'NOT TESTED'
        if mongodb_uri != 'NOT SET':
            try:
                from pymongo import MongoClient
                client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
                client.admin.command('ping')
                db_status = '✅ Connection successful'
                client.close()
            except Exception as e:
                db_status = f'❌ Connection failed: {str(e)}'
        
        # Test app import
        app_import_status = 'NOT TESTED'
        try:
            # Try importing our main app components
            from config import Config
            app_import_status = '✅ Config imported successfully'
            
            from models import User
            app_import_status += ', Models imported'
            
            from forms import LoginForm
            app_import_status += ', Forms imported'
            
        except Exception as e:
            app_import_status = f'❌ Import failed: {str(e)}'
        
        html = f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>AgriConnect - Diagnostic Report</title>
            <style>
                body {{ font-family: monospace; margin: 40px; background: #f5f5f5; }}
                .container {{ background: white; padding: 30px; border-radius: 8px; max-width: 800px; }}
                .success {{ color: #28a745; }}
                .error {{ color: #dc3545; }}
                .warning {{ color: #ffc107; }}
                .section {{ margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #007bff; }}
                pre {{ background: #e9ecef; padding: 10px; border-radius: 4px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔍 AgriConnect MVP - Diagnostic Report</h1>
                
                <div class="section">
                    <h3>📊 System Information</h3>
                    <p><strong>Python Version:</strong> {python_version}</p>
                    <p><strong>Current Working Directory:</strong> {os.getcwd()}</p>
                    <p><strong>Available Files:</strong> {', '.join(os.listdir('.'))}</p>
                </div>
                
                <div class="section">
                    <h3>🌍 Environment Variables</h3>
                    <p><strong>MONGODB_URI:</strong> <span class="{'success' if mongodb_uri != 'NOT SET' else 'error'}">{mongodb_uri[:50]}{'...' if len(mongodb_uri) > 50 else ''}</span></p>
                    <p><strong>SECRET_KEY:</strong> <span class="{'success' if secret_key != 'NOT SET' else 'error'}">{secret_key[:20] + '...' if secret_key != 'NOT SET' else 'NOT SET'}</span></p>
                </div>
                
                <div class="section">
                    <h3>📦 Module Import Status</h3>
        '''
        
        for module, status in import_status.items():
            html += f'<p><strong>{module}:</strong> {status}</p>'
        
        html += f'''
                </div>
                
                <div class="section">
                    <h3>🗄️ Database Connection</h3>
                    <p><strong>Status:</strong> {db_status}</p>
                </div>
                
                <div class="section">
                    <h3>🚀 Application Import</h3>
                    <p><strong>Status:</strong> {app_import_status}</p>
                </div>
                
                <div class="section">
                    <h3>🔧 Next Steps</h3>
                    <p>If you see any ❌ above, that's likely the cause of your 500 error.</p>
                    <p><a href="/test-simple-app" style="background:#007bff;color:white;padding:10px;text-decoration:none;border-radius:4px;">Test Simple App</a></p>
                </div>
            </div>
        </body>
        </html>
        '''
        
        return html
        
    except Exception as e:
        return f'''
        <html>
        <body style="font-family:monospace;margin:40px;">
            <h1>🚨 Critical Error</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        '''

@app.route('/test-simple-app')
def test_simple_app():
    """Test if we can load the actual app"""
    try:
        # Set default environment variables if missing
        if not os.environ.get('MONGODB_URI'):
            os.environ['MONGODB_URI'] = 'mongodb+srv://priyapremnmkl5:mlBObqUYLnQK0WUf@agriconnect.2clc19t.mongodb.net/agri_connect_db?retryWrites=true&w=majority&appName=AgriConnect'
        if not os.environ.get('SECRET_KEY'):
            os.environ['SECRET_KEY'] = 'KgxxSH0ChsvTxm4qVM6XCAi6JPenycLWPIEBfNrg8mI'
            
        # Try to import and run the main app
        from app import app as main_app
        return f'''
        <html>
        <body style="font-family:monospace;margin:40px;">
            <h1>✅ Success!</h1>
            <p>Main application imported successfully!</p>
            <p><a href="/switch-to-main">Switch to Main App</a></p>
        </body>
        </html>
        '''
        
    except Exception as e:
        return f'''
        <html>
        <body style="font-family:monospace;margin:40px;">
            <h1>❌ Main App Import Failed</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        '''

@app.route('/switch-to-main')
def switch_to_main():
    """Switch to the main application"""
    try:
        # Set environment variables
        if not os.environ.get('MONGODB_URI'):
            os.environ['MONGODB_URI'] = 'mongodb+srv://priyapremnmkl5:mlBObqUYLnQK0WUf@agriconnect.2clc19t.mongodb.net/agri_connect_db?retryWrites=true&w=majority&appName=AgriConnect'
        if not os.environ.get('SECRET_KEY'):
            os.environ['SECRET_KEY'] = 'KgxxSH0ChsvTxm4qVM6XCAi6JPenycLWPIEBfNrg8mI'
            
        # Import and replace this app with the main app
        from app import app as main_app
        # Copy routes from main app
        return main_app.test_client().get('/').get_data(as_text=True)
        
    except Exception as e:
        return f'''
        <html>
        <body style="font-family:monospace;margin:40px;">
            <h1>❌ Failed to Switch to Main App</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        '''

@app.route('/health')
def health():
    return jsonify({
        'status': 'diagnostic_mode',
        'message': 'Running diagnostic version',
        'python_version': sys.version,
        'env_vars_set': {
            'MONGODB_URI': bool(os.environ.get('MONGODB_URI')),
            'SECRET_KEY': bool(os.environ.get('SECRET_KEY'))
        }
    })

# Export for Vercel
application = app

if __name__ == '__main__':
    app.run(debug=True)
