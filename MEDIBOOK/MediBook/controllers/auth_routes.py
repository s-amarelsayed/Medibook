from flask import Blueprint, render_template, redirect, url_for, request, session, flash, current_app
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from repositories import UserRepository, PatientRepository, ClinicRepository
from models.user_model import User
from flask_login import current_user
import os
import re
import uuid
from datetime import datetime

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
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')

        if not all([name, email, password, confirm_password, role]):
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('auth.register'))

        if len(password) < 8:
            flash('Password must be at least 8 characters long.', 'danger')
            return redirect(url_for('auth.register'))

        if not re.search(r'[A-Z]', password):
            flash('Password must contain at least one uppercase letter (A-Z).', 'danger')
            return redirect(url_for('auth.register'))

        if not re.search(r'[a-z]', password):
            flash('Password must contain at least one lowercase letter (a-z).', 'danger')
            return redirect(url_for('auth.register'))

        if not re.search(r'\d', password):
            flash('Password must contain at least one number (0-9).', 'danger')
            return redirect(url_for('auth.register'))

        if not re.search(r'[!@#$%^&*]', password):
            flash('Password must contain at least one special character (!@#$%^&*).', 'danger')
            return redirect(url_for('auth.register'))

        if UserRepository.get_by_email(email):
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = generate_password_hash(password)
        verified = False if role == 'doctor' else True

        profile_picture = 'default.png'
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                profile_picture = unique_filename

        try:
            new_user = UserRepository.create(
                name=name,
                email=email,
                password_hash=hashed_password,
                role=role,
                verified=verified,
                profile_picture=profile_picture
            )
            UserRepository.flush()

            if role == 'patient':
                dob_str = request.form.get('dob')
                phone = request.form.get('phone')
                if not dob_str or not phone:
                    UserRepository.rollback()
                    flash('Date of birth and phone are required for patients.', 'danger')
                    return redirect(url_for('auth.register'))

                try:
                    dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                except ValueError:
                    UserRepository.rollback()
                    flash('Invalid date of birth.', 'danger')
                    return redirect(url_for('auth.register'))

                PatientRepository.create(user_id=new_user.user_id, dob=dob, phone=phone)

            UserRepository.commit()
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('auth.login'))

        except IntegrityError:
            UserRepository.rollback()
            flash('An error occurred. Please try again.', 'danger')
            return redirect(url_for('auth.register'))

    clinics = ClinicRepository.get_all()
    return render_template('register.html', clinics=clinics)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return redirect(url_for('auth.login'))

        user = UserRepository.get_by_email(email)

        if user and check_password_hash(user.password_hash, password):
            if user.role == 'doctor' and not user.verified:
                flash('Your doctor account is pending admin approval. Please wait.', 'warning')
                return redirect(url_for('auth.login'))

            session['user_id'] = user.user_id
            session['role'] = user.role
            session['name'] = user.name
            session['profile_picture'] = user.profile_picture or 'default.png'

            flash(f'Welcome back, {user.name}!', 'success')
            return redirect(url_for('doctor.search'))

        flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = UserRepository.get_by_id(session['user_id'])

    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        name = request.form.get('name')

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                filepath = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles', unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                user.profile_picture = unique_filename

        user.name = name

        # Save medical history if patient
        if user.role == 'patient' and user.patient:
            medical_history = request.form.get('medical_history', '')
            user.patient.medical_history = medical_history

        UserRepository.commit()
        session['name'] = name
        session['profile_picture'] = user.profile_picture or 'default.png'

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('booking.dashboard'))

    from datetime import date
    return render_template('edit_profile.html', user=user, today=date.today())