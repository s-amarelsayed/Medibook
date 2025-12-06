from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db
from models.user_model import User, Patient, Doctor
import os

auth_bp = Blueprint('auth', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('auth.register'))
            
        hashed_password = generate_password_hash(password)
        
        # Set verified=False for doctors, True for others
        verified = False if role == 'doctor' else True
        
        # Handle profile picture upload
        profile_picture = 'default.png'
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create unique filename
                import uuid
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join('static', 'uploads', 'profiles', unique_filename)
                file.save(filepath)
                profile_picture = unique_filename
        
        new_user = User(name=name, email=email, password_hash=hashed_password, role=role, verified=verified, profile_picture=profile_picture)
        db.session.add(new_user)
        db.session.commit()
        
        try:
            if role == 'patient':
                dob_str = request.form.get('dob')
                phone = request.form.get('phone')
                
                if not dob_str:
                    flash('Date of birth is required for patients')
                    db.session.delete(new_user)
                    db.session.commit()
                    return redirect(url_for('auth.register'))
                
                from datetime import datetime
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                new_patient = Patient(user_id=new_user.user_id, dob=dob, phone=phone)
                db.session.add(new_patient)
                
            elif role == 'doctor':
                from models.appointment_model import Clinic
                
                specialization = request.form.get('specialization')
                price = request.form.get('price')
                clinic_name = request.form.get('clinic_name')
                clinic_address = request.form.get('clinic_address')
                clinic_city = request.form.get('clinic_city')
                clinic_country = request.form.get('clinic_country')
                clinic_phone = request.form.get('clinic_phone')
                
                if not specialization or not price or not clinic_name or not clinic_city or not clinic_country:
                    flash('All doctor and clinic fields are required')
                    db.session.delete(new_user)
                    db.session.commit()
                    return redirect(url_for('auth.register'))
                
                # Create new clinic for this doctor
                new_clinic = Clinic(
                    name=clinic_name,
                    address=clinic_address or '',
                    city=clinic_city,
                    country=clinic_country,
                    phone=clinic_phone or ''
                )
                db.session.add(new_clinic)
                db.session.commit()
                
                new_doctor = Doctor(
                    user_id=new_user.user_id,
                    specialization=specialization,
                    price=float(price),
                    clinic_id=new_clinic.clinic_id
                )
                db.session.add(new_doctor)
                
            db.session.commit()
            
            if role == 'doctor':
                flash('Registration successful! Your account is pending admin approval. You will be able to login once approved.')
            else:
                flash('Registration successful. Please login.')
            
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}')
            return redirect(url_for('auth.register'))
        
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            # Check if doctor is verified
            if user.role == 'doctor' and not user.verified:
                flash('Your account is pending admin approval. Please wait for verification.')
                return redirect(url_for('auth.login'))
            
            session['user_id'] = user.user_id
            session['role'] = user.role
            session['name'] = user.name
            return redirect(url_for('doctor.search'))
            
        flash('Invalid email or password')
        
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
