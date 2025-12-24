from flask import Flask
from config import Config
from models import db, login_manager
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
# Import models to ensure they are registered with SQLAlchemy
from models.user_model import User, Patient, Doctor
from models.appointment_model import Clinic, Appointment, DoctorAvailability, Review

def create_app(config_class=Config):
    """
    App Factory Pattern Implementation.
    Creates and configures an instance of the Flask application.
    This allows for creating multiple instances with different configurations (e.g., testing vs production).
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    from database_singleton import db_singleton
    db_singleton.initialize(db)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        # Drop all tables and recreate to ensure schema is up to date
        db.drop_all()
        db.create_all()

    from controllers.auth_routes import auth_bp
    from controllers.doctor_routes import doctor_bp
    from controllers.booking_routes import booking_bp
    from controllers.admin_routes import admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(doctor_bp) # Main routes usually at root or /doctor, keeping as is for home search
    app.register_blueprint(booking_bp, url_prefix='/booking')
    
    from controllers.chat_routes import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/chat')
    
    app.register_blueprint(admin_bp)

    return app

def seed_database():
    from models.user_model import User, Doctor, Patient
    from models.appointment_model import Clinic
    from werkzeug.security import generate_password_hash
    from datetime import datetime

    try:
        if User.query.first():
            print("Database already seeded.")
            return

        print("Seeding database...")
        
        # Admin
        admin = User(name='Admin User', email='admin@medibook.com', password_hash=generate_password_hash('admin123'), role='admin', verified=True)
        db.session.add(admin)

        # Clinics
        clinic1 = Clinic(name='NileClinic', address='123 Nile St', city='Cairo', country='Egypt', phone='01000000001')
        clinic2 = Clinic(name='CityMed', address='456 City Rd', city='Giza', country='Egypt', phone='01000000002')
        db.session.add_all([clinic1, clinic2])
        db.session.commit()

        # Doctors
        doc_user1 = User(name='Dr. Ayman', email='ayman@medibook.com', password_hash=generate_password_hash('doctor123'), role='doctor', verified=True)
        doc_user2 = User(name='Dr. Mona', email='mona@medibook.com', password_hash=generate_password_hash('doctor123'), role='doctor', verified=True)
        db.session.add_all([doc_user1, doc_user2])
        db.session.commit()

        doctor1 = Doctor(user_id=doc_user1.user_id, clinic_id=clinic1.clinic_id, specialization='Cardiologist', bio='Expert in heart.', price=500.0)
        doctor2 = Doctor(user_id=doc_user2.user_id, clinic_id=clinic2.clinic_id, specialization='Dermatologist', bio='Skin specialist.', price=300.0)
        db.session.add_all([doctor1, doctor2])

        # Patient
        patient_user = User(name='Ali Patient', email='ali@medibook.com', password_hash=generate_password_hash('patient123'), role='patient')
        db.session.add(patient_user)
        db.session.commit()

        patient1 = Patient(user_id=patient_user.user_id, dob=datetime.strptime('1990-01-01', '%Y-%m-%d').date(), phone='01200000000')
        db.session.add(patient1)
        
        db.session.commit()
        print("Database seeded successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()
    app.run(debug=True)
