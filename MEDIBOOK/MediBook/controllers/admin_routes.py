from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from repositories import PatientRepository, DoctorRepository, AppointmentRepository, UserRepository

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

#phase5: Admin Dashboard for verification and stats
@admin_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('Access denied. Admin only.')
        return redirect(url_for('auth.login'))
        
    # Stats
    total_patients = PatientRepository.count()
    total_doctors = DoctorRepository.count()
    total_appointments = AppointmentRepository.count()
    
    # Unverified doctors
    unverified_doctors = DoctorRepository.get_unverified()
    
    return render_template('admin/dashboard.html', 
                         total_patients=total_patients, 
                         total_doctors=total_doctors, 
                         total_appointments=total_appointments,
                         unverified_doctors=unverified_doctors)

#phase5: Verify Doctor Action
@admin_bp.route('/verify_doctor/<int:doctor_id>', methods=['POST'])
def verify_doctor(doctor_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    doctor = DoctorRepository.get_by_id(doctor_id)
    if not doctor:
        flash('Doctor not found.')
        return redirect(url_for('admin.dashboard'))
        
    user = UserRepository.get_by_id(doctor.user_id)
    if user:
        user.verified = True
        UserRepository.commit()
        flash(f'Doctor {user.name} verified successfully.')
    return redirect(url_for('admin.dashboard'))

#phase5: Delete User logic (Bonus?)
@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    user = UserRepository.get_by_id(user_id)
    if user:
        from database_singleton import db_singleton
        db_singleton.session.delete(user)
        UserRepository.commit()
    flash('User deleted.')
    return redirect(url_for('admin.dashboard'))
