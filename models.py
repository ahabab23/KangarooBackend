from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()
class UserRole(enum.Enum):
    Admin = 'Admin'
    Publisher = 'Publisher'
    Content_Creator = 'Content Creator'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email_address = db.Column(db.String(120), unique=True, nullable=False)
    telephone_number = db.Column(db.String(50))
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.Admin)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f"<User {self.full_name} - {self.role.value}>"
    def to_dict(self):
            return {
                'id': self.id,
                'full_name': self.full_name,
                'email_address': self.email_address,
                'telephone_number': self.telephone_number,
                'role': self.role.value,
                'created_at': self.created_at.isoformat()
            }


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    published=db.Column(db.DateTime)
    category = db.Column(db.String(100))
    status = db.Column(db.Enum('Pending', 'Ongoing', 'Completed', name='project_status'), nullable=False, default='Pending')
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def formatted_published(self):
        return self.published.strftime('%B %d, %Y') 

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email_address = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
class MissionVision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(200))  # Icon can be a class name or URL
    text = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))  # Optional supporting image


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=False)
    image_url = db.Column(db.String(500))  # Profile image


class Header(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(500), nullable=False)
    subtitle = db.Column(db.String(200))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50))
    image_url = db.Column(db.String(500))  # Google Maps link or embedded map iframe URL
