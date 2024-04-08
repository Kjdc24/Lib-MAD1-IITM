from dotenv import load_dotenv
from os import getenv
from app import app

load_dotenv()

# Set Flask configuration variables
app.config['FLASK_DEBUG'] = getenv('FLASK_DEBUG')
app.config['FLASK_APP'] = getenv('FLASK_APP')

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = getenv('SQLALCHEMY_DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
app.config['SECRET_KEY'] = getenv('SECRET_KEY')

print("Successfully Configured")