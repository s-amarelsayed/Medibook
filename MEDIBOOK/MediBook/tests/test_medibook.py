"""
Unified Unit Test Suite for MediBook
Tests for: Authentication, Search, Booking, AI Chat, 
And Architectural Patterns (Singleton, Repository)
"""
import sys
import os
import pytest
from datetime import date

# Ensure the parent directory (MediBook) is in the path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from config import Config
from models.user_model import User, Doctor, Patient
from models.appointment_model import Clinic, DoctorAvailability, Review
from repositories import UserRepository, DoctorRepository, ClinicRepository, AvailabilityRepository, ReviewRepository
from database_singleton import DatabaseSingleton, db_singleton
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    """Create test app with isolated database"""
    class TestConfig(Config):
        TESTING = True
        SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        WTF_CSRF_ENABLED = False
        
    app = create_app(TestConfig)
    
    # Ensure Singleton is initialized
    db_singleton.initialize(db)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()

@pytest.fixture
def auth_client(client, app):
    """Register and login a user for authenticated tests."""
    with app.app_context():
        client.post('/auth/register', data={
            'name': 'Test User',
            'email': 'test@test.com',
            'password': 'password',
            'role': 'patient',
            'dob': '2000-01-01',
            'phone': '1234567890'
        })
        client.post('/auth/login', data={
            'email': 'test@test.com',
            'password': 'password'
        })
    return client

# ============================================
# BASIC CORE TESTS (Original Phase 1-4)
# ============================================

def test_home_page(client):
    """Test that home page loads correctly."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"MediBook" in response.data

def test_registration(client):
    """Test user registration."""
    response = client.post('/auth/register', data={
        'name': 'New User',
        'email': 'new@test.com',
        'password': 'password',
        'role': 'patient',
        'dob': '1990-01-01',
        'phone': '0987654321'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Registration successful" in response.data

def test_login_logout(client):
    """Test login and logout flow."""
    client.post('/auth/register', data={
        'name': 'Login User',
        'email': 'login@test.com',
        'password': 'password',
        'role': 'patient',
        'dob': '1990-01-01',
        'phone': '1112223333'
    })
    
    response = client.post('/auth/login', data={
        'email': 'login@test.com',
        'password': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data or b"Search" in response.data
    
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"Login" in response.data

def test_search_page_elements(client):
    """Test doctor search page functionality."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Specialization" in response.data

def test_admin_access_denied(client):
    """Test that non-admin cannot access admin dashboard."""
    client.post('/auth/register', data={
        'name': 'Normal User',
        'email': 'normal@test.com',
        'password': 'password',
        'role': 'patient',
        'dob': '2000-01-01',
        'phone': '1231231234'
    })
    client.post('/auth/login', data={'email': 'normal@test.com', 'password': 'password'})
    
    response = client.get('/admin/dashboard', follow_redirects=True)
    assert b"Login" in response.data or b"Access denied" in response.data or b"Search" in response.data

def test_booking_protection(client):
    """Test that booking endpoint requires login."""
    response = client.post('/booking/book/1', follow_redirects=True)
    assert b"login" in response.data.lower()

# ============================================
# SINGLETON PATTERN TESTS (Bonus Requirement)
# ============================================

def test_singleton_single_instance():
    """Test that DatabaseSingleton returns the same instance."""
    instance1 = DatabaseSingleton()
    instance2 = DatabaseSingleton()
    assert instance1 is instance2

def test_singleton_initialization(app):
    """Test that Singleton properly initializes with database."""
    with app.app_context():
        db_instance = db_singleton.get_db()
        assert db_instance is not None

# ============================================
# REPOSITORY PATTERN TESTS (Bonus Requirement)
# ============================================

def test_user_repository_create(app):
    """Test UserRepository.create method."""
    with app.app_context():
        user = UserRepository.create(
            name="Repo User",
            email="repo@test.com",
            password_hash=generate_password_hash("pass"),
            role="patient"
        )
        db.session.commit()
        assert user.name == "Repo User"
        assert UserRepository.get_by_email("repo@test.com") is not None

def test_doctor_repository_search(app):
    """Test DoctorRepository.search method."""
    with app.app_context():
        clinic = Clinic(name="C1", address="A1", city="Cairo", country="Egypt", phone="123")
        db.session.add(clinic)
        db.session.commit()
        
        user = User(name="Dr. X", email="x@test.com", password_hash="pass", role="doctor", verified=True)
        db.session.add(user)
        db.session.commit()
        
        doctor = Doctor(user_id=user.user_id, clinic_id=clinic.clinic_id, specialization="Cardio", bio="B", price=100)
        db.session.add(doctor)
        db.session.commit()
        
        results = DoctorRepository.search(specialization="Cardio")
        assert len(results) == 1

# ============================================
# AI CHAT FEATURE TESTS (Bonus Requirement)
# ============================================

def test_chat_response_structure(client):
    """Test that chat endpoint returns valid JSON structure."""
    response = client.post('/chat/message', json={'message': 'hello'}, content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert 'response' in data
    assert 'MediBook AI Assistant' in data['response']

def test_chat_medical_fallback(client):
    """Test that chat returns medical advice from fallback system."""
    response = client.post('/chat/message', json={'message': 'headache'}, content_type='application/json')
    data = response.get_json()
    assert 'Acetaminophen' in data['response'] or 'quiet, dark room' in data['response']
