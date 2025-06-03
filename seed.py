from app import app
from models import db, User, Post, Contact
import json
import os
from datetime import datetime

# Load posts from JSON
json_path = os.path.join(os.path.dirname(__file__), './projects.json')
with open(json_path, 'r') as f:
    projects_data = json.load(f)

with app.app_context():
    print("Deleting existing users and posts...")
    User.query.delete()
    Post.query.delete()
    Contact.query.delete()
    db.session.commit()

    db.create_all()

    # Create Users
    admin = User(
        full_name='Adm2in',
        email_address='admin1@example.com',
        telefone_number='00000002000',
        role='Admin',
    )
    admin.set_password('adminp2ass')

    editor = User(
        full_name='Jane Editor',
        email_address='jane.editor@example.com',
        telefone_number='1234567890',
        role='Admin'
    )
    editor.set_password('editorpass')

    viewer = User(
        full_name='Bob Vi3ewer',
        email_address='bob.vi2ewer@example.com',
        telefone_number='09287654321',
        role='Viewer'
    )
    viewer.set_password('viewerpass')

    db.session.add_all([admin, editor, viewer])
    db.session.commit()
    print('Seeded 3 users.')

    # Create Posts from JSON
    def parse_date(date_str):
        if not date_str:
            return None
        try:
            # Try parsing "June 18, 2019" format
            return datetime.strptime(date_str, '%B %d, %Y')
        except ValueError:
            # You can add more formats or return None
            return None
    post_objects = []
    for project in projects_data:
        published_str = project.get('Published',"")
        published_date = parse_date(published_str)
        post = Post(
            id=project.get('Id'),
            title=project.get('Title'),
            description=project.get('Description'),
            published=published_date,
            category=project.get('Category'),
            client=project.get('Client',),
            image_url=project.get('Imageurl') # Support both keys
        )
        post_objects.append(post)

    db.session.add_all(post_objects)
    db.session.commit()
    print(f'Seeded {len(post_objects)} posts from JSON.')

    # Create Contacts
    contact1 = Contact(
        name='Alice Customer',
        email_address='alice.customer@example.com',
        message='I have a question about your pricing plans.'
    )

    contact2 = Contact(
        name='Tom Prospect',
        email_address='tom.prospect@example.com',
        message='Can you send me a demo of the product?'
    )

    contact3 = Contact(
        name='Sara Feedback',
        email_address='sara.feedback@example.com',
        message='Great website! Just wanted to say thanks.'
    )

    db.session.add_all([contact1, contact2, contact3])
    db.session.commit()
    print('Seeded 3 contacts.')
