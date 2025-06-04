from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import jwt
import os
from functools import wraps
from datetime import datetime, timedelta
from models import db, User, Post, Contact
import datetime
from flask_migrate import Migrate
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize SQLAlchemy and Migrate
db.init_app(app)
migrate = Migrate(app, db)

bcrypt = Bcrypt(app)
CORS(app)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['id'])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email_address=data["email"]).first()

    if user and user.check_password(data["password"]):
        # Create a JWT that expires in 2 hours
        token = jwt.encode(
            {
                "id": user.id,
                "exp": datetime.utcnow() + timedelta(hours=2),
            },
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        return jsonify({"token": token})

    return jsonify({"message": "Invalid credentials"}), 401
# User Endpoints
@app.route('/api/users', methods=['GET'])
@token_required
def get_users(current_user):
    users = User.query.all()
    output = [{
        'id': u.id,
        'full_name': u.full_name,
        'email_address': u.email_address,
        'telefone_number': u.telefone_number,
        'role': u.role
    } for u in users]
    return jsonify(output)

@app.route('/api/users', methods=['POST'])
@token_required
def create_user(current_user):
    data = request.json
    new_user = User(
        full_name=data['full_name'],
        email_address=data['email_address'],
        telefone_number=data.get('telefone_number', ''),
        role=data.get('role', 'Admin')
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'New user created'}), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(current_user, user_id):
    data = request.json
    user = User.query.get_or_404(user_id)
    user.full_name = data['full_name']
    user.email_address = data['email_address']
    user.telefone_number = data.get('telefone_number', user.telefone_number)
    if data.get('password'):
        user.set_password(data['password'])
    user.role = data.get('role', user.role)
    db.session.commit()
    return jsonify({'message': 'User updated'})

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(current_user, user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User deleted'})

# Post Endpoints
@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    output = [p.__dict__ for p in posts]
    for p in output:
        p.pop('_sa_instance_state', None)
    return jsonify(output)


@app.route('/api/posts', methods=['POST'])
@token_required
def create_post(current_user):
    data = request.json
    published_str = data.get('published')
    
    # Handle empty published date
    if published_str:
        try:
            # Convert from frontend format (June 18, 2019) to datetime
            published_date = datetime.strptime(published_str, "%B %d, %Y")
        except ValueError:
            published_date = None
    else:
        published_date = None

    new_post = Post(
        title=data['title'],
        description=data['description'],
        published=published_date,
        category=data.get('category', ''),
        client=data.get('client', ''),
        image_url=data.get('image_url', '')
    )
    
    db.session.add(new_post)
    db.session.commit()
    return jsonify({'message': 'Post created'}), 201


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(current_user, post_id):
    data = request.json
    post = Post.query.get_or_404(post_id)
    
    published_str = data.get('published')
    if published_str:
        try:
            # Convert from frontend format (June 18, 2019) to datetime
            published_date = datetime.strptime(published_str, "%B %d, %Y")
        except ValueError:
            published_date = post.published  # Keep existing if conversion fails
    else:
        published_date = None

    post.title = data['title']
    post.description = data['description']
    post.published = published_date  # Use converted datetime object
    post.category = data.get('category', post.category)
    post.client = data.get('client', post.client)
    post.image_url = data.get('image_url', post.image_url)
    
    db.session.commit()
    return jsonify({'message': 'Post updated'})

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    output = {
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'published': post.published.strftime("%B %d, %Y") if post.published else None,
        'category': post.category,
        'client': post.client,
        'image_url': post.image_url
    }
    return jsonify(output)

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted'})

# Contact Endpoints
@app.route('/api/contacts', methods=['GET'])
@token_required
def get_contacts(current_user):
    contacts = Contact.query.order_by(Contact.date.desc()).all()
    output = [{
        'id': c.id,
        'name': c.name,
        'email_address': c.email_address,
        'message': c.message,
        'date': c.date.strftime('%Y-%m-%d %H:%M:%S')
    } for c in contacts]
    return jsonify(output)

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    data = request.json
    new_contact = Contact(
        name=data['name'],
        email_address=data['email_address'],
        message=data['message']
    )
    db.session.add(new_contact)
    db.session.commit()
    return jsonify({'message': 'Contact submitted'}), 201

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
