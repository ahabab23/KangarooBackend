from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from functools import wraps
from datetime import datetime, timedelta
import jwt
import os

from models import db, User, Post, Contact,MissionVision,Team,Header,Address

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://admin:Uwes20252025@app.cp4qq4kwm5xp.eu-north-1.rds.amazonaws.com:3306/app"
)
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
CORS(app)
migrate = Migrate(app, db)

# JWT token required decorator
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
            if not current_user:
                raise Exception('User not found')
        except Exception:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

# Login route
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    email = data.get("email_address")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email_address=email).first()
    if user and user.check_password(password):
        token = jwt.encode(
            {"id": user.id, "exp": datetime.utcnow() + timedelta(hours=2)},
            app.config["SECRET_KEY"],
            algorithm="HS256"
        )
        return jsonify({"token": token})
    
    return jsonify({"message": "Invalid credentials"}), 401

# ---------------- User Routes ----------------

@app.route('/api/users', methods=['GET'])
@token_required
def get_users(current_user):
    users = User.query.all()
    return jsonify([u.to_dict() for u in users])

@app.route('/api/users', methods=['POST'])
@token_required
def create_user(current_user):
    data = request.json
    new_user = User(
        full_name=data['full_name'],
        email_address=data['email_address'],
        telephone_number=data.get('telephone_number', ''),
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
    user.telephone_number = data.get('telephone_number', user.telephone_number)
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

# ---------------- Post Routes ----------------

@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = Post.query.all()
    output = []
    for post in posts:
        output.append({
            'id': post.id,
            'title': post.title,
            'description': post.description,
            'published': post.formatted_published if post.published else None,
            'category': post.category,
            'status': post.status,
            'image_url': post.image_url,
            'created_at': post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
        })
    return jsonify(output)

@app.route('/api/posts', methods=['POST'])
@token_required
def create_post(current_user):
    data = request.json
    published = None
    if data.get('published'):
        try:
            published = datetime.strptime(data['published'], "%B %d, %Y")
        except ValueError:
            pass
    new_post = Post(
        title=data['title'],
        description=data['description'],
        published=published,
        category=data.get('category'),
        status=data.get('status', 'Pending'),
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
    if data.get('published'):
        try:
            post.published = datetime.strptime(data['published'], "%B %d, %Y")
        except ValueError:
            pass
    post.title = data['title']
    post.description = data['description']
    post.category = data.get('category', post.category)
    post.status = data.get('status', post.status)
    post.image_url = data.get('image_url', post.image_url)
    db.session.commit()
    return jsonify({'message': 'Post updated'})

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify({
        'id': post.id,
        'title': post.title,
        'description': post.description,
        'published': post.formatted_published if post.published else None,
        'category': post.category,
        'status': post.status,
        'image_url': post.image_url
    })

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post deleted'})

# ---------------- Contact Routes ----------------

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

@app.route('/api/mission-vision', methods=['GET'])
def get_mission_vision():
    records = MissionVision.query.all()
    output = []

    for mv in records:
        output.append({
            'id': mv.id,
            'title': mv.title,
            'icon': mv.icon,
            'text': mv.text,
            'image_url': mv.image_url
        })

    return jsonify(output)


@app.route('/api/mission-vision', methods=['PUT'])
@token_required
def update_mission_vision(current_user):
    data = request.json
    mv = MissionVision.query.get(data.get("id"))  # Ensure you're passing the correct ID from frontend

    if not mv:
        return jsonify({'message': 'Mission/Vision not found'}), 404

    mv.title = data.get('title', mv.title)
    mv.icon = data.get('icon', mv.icon)
    mv.text = data.get('text', mv.text)
    mv.image_url = data.get('image_url', mv.image_url)

    db.session.commit()
    return jsonify({'message': 'Mission and Vision updated'})

@app.route('/api/team', methods=['POST'])
@token_required
def create_team_member(current_user):
    data = request.json
    member = Team(
        name=data['name'],
        position=data['position'],
        image_url=data.get('image_url', '')
    )
    db.session.add(member)
    db.session.commit()
    return jsonify({'message': 'Team member added'}), 201

@app.route('/api/team/<int:member_id>', methods=['PUT'])
@token_required
def update_team_member(current_user, member_id):
    data = request.json
    member = Team.query.get_or_404(member_id)
    member.name = data['name']
    member.position = data['position']
    member.image_url = data.get('image_url', member.image_url)
    db.session.commit()
    return jsonify({'message': 'Team member updated'})

@app.route('/api/team/<int:member_id>', methods=['DELETE'])
@token_required
def delete_team_member(current_user, member_id):
    member = Team.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'message': 'Team member deleted'})
@app.route('/api/headers', methods=['POST'])
@token_required
def create_header(current_user):
    data = request.json
    header = Header(
        title=data['title'],
        subtitle=data['subtitle'],
        description=data['description'],
        image_url=data.get('image_url', '')
    )
    db.session.add(header)
    db.session.commit()
    return jsonify({'message': 'Header created'}), 201

@app.route('/api/headers/<int:header_id>', methods=['PUT'])
@token_required
def update_header(current_user, header_id):
    data = request.json
    header = Header.query.get_or_404(header_id)
    header.title = data['title']
    header.subtitle = data['subtitle']
    header.description = data['description']
    header.image_url = data.get('image_url', header.image_url)
    db.session.commit()
    return jsonify({'message': 'Header updated'})

@app.route('/api/headers/<int:header_id>', methods=['DELETE'])
@token_required
def delete_header(current_user, header_id):
    header = Header.query.get_or_404(header_id)
    db.session.delete(header)
    db.session.commit()
    return jsonify({'message': 'Header deleted'})

@app.route('/api/team', methods=['GET'])
def get_all_team_members():
    members = Team.query.all()
    return jsonify([
        {
            'id': m.id,
            'name': m.name,
            'position': m.position,
            'image_url': m.image_url
        } for m in members
    ])

@app.route('/api/team/<int:member_id>', methods=['GET'])
def get_team_member(member_id):
    m = Team.query.get_or_404(member_id)
    return jsonify({
        'id': m.id,
        'full_name': m.full_name,
        'position': m.position,
        'image_url': m.image_url
    })
@app.route('/api/headers', methods=['GET'])
def get_all_headers():
    headers = Header.query.all()
    return jsonify([
        {
            'id': h.id,
            'title': h.title,
            'subtitle':h.subtitle,
            'description': h.description,
            'image_url': h.image_url
        } for h in headers
    ])

@app.route('/api/headers/<int:header_id>', methods=['GET'])
def get_header(header_id):
    h = Header.query.get_or_404(header_id)
    return jsonify({
        'id': h.id,
        'title': h.title,
        'description': h.description,
        'image_url': h.image_url
    })
@app.route('/api/addresses', methods=['GET'])
def get_all_addresses():
    addresses = Address.query.all()
    return jsonify([
        {
            'id': a.id,
            'office_address': a.office_address,
            'email': a.email,
            'phone': a.phone
        } for a in addresses
    ])

@app.route('/api/addresses/<int:address_id>', methods=['GET'])
def get_address(address_id):
    a = Address.query.get_or_404(address_id)
    return jsonify({
        'id': a.id,
        'office_address': a.office_address,
        'email': a.email,
        'phone': a.phone
    })



# ---------------- Run App ----------------

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
