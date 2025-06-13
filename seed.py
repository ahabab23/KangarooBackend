import json
from datetime import datetime
from app import app, db  # Make sure app is imported here
from models import User, Contact, Address, Post, Header, MissionVision, Team, UserRole
from dateutil import parser
def load_json(filename):
    with open(filename, "r") as f:
        return json.load(f)

def seed_users():
    user = User(
        full_name="Admin User",
        email_address="admin@example.com",
        telephone_number="1234567890",
        role=UserRole.Admin
    )
    user.set_password("securepassword")
    user = User(
        full_name="Uwes Yere",
        email_address="uwes@gmail.com",
        telephone_number="1234567890",
        role=UserRole.Admin
    )
    user.set_password("Uwes@2025")
    db.session.add(user)

def seed_contacts():
    contact = Contact(
        name="John Doe",
        email_address="john@example.com",
        message="I'd love to know more about your services!"
    )
    db.session.add(contact)
def seed_from_json(model, filename):
    data = load_json(filename)
    for entry in data:
        # Remove keys not in the model
        valid_keys = {col.name for col in model.__table__.columns}
        filtered_entry = {k: v for k, v in entry.items() if k in valid_keys}

        # Convert published to datetime if it's for Post
        if model == Post and 'published' in filtered_entry:
            try:
                filtered_entry['published'] = parser.parse(filtered_entry['published'])
            except Exception as e:
                print(f"⚠️ Could not parse published date '{filtered_entry['published']}': {e}")
                continue

        db.session.add(model(**filtered_entry))

def seed_addresses():
    address = Address(
        location="123 Innovation Way, Nairobi, Kenya",
        email="info@example.com",
        phone="+254700000000",
        image_url="https://maps.example.com/embed/map-location"
    )
    db.session.add(address)



def run_seed():
    with app.app_context():  # ✅ Ensure the app context is active
        db.drop_all()
        db.create_all()

        # Seed from JSON
        seed_from_json(Post, "./posts.json")
        seed_from_json(Header, "./header.json")
        seed_from_json(MissionVision, "./missionVission.json")
        seed_from_json(Team, "./team.json")

        # Seed manually
        seed_users()
        seed_contacts()
        seed_addresses()

        db.session.commit()
        print("✅ Database seeded successfully!")

if __name__ == "__main__":
    run_seed()
