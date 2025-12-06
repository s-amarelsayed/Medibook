from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.user_model import User, Doctor, Patient
from models.appointment_model import Appointment, DoctorAvailability
from datetime import datetime, time, date

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book/<int:doctor_id>', methods=['POST'])
def book_appointment(doctor_id):
    if 'user_id' not in session or session.get('role') != 'patient':
        flash('Please login as a patient to book an appointment.')
        return redirect(url_for('auth.login'))

    doctor = Doctor.query.get_or_404(doctor_id)
    patient = Patient.query.filter_by(user_id=session['user_id']).first()
    
    if not patient:
        flash('Patient profile not found.')
        return redirect(url_for('doctor.profile', doctor_id=doctor_id))
    
    availability_id = request.form.get('availability_id')
    payment_method = request.form.get('payment_method')
    
    if not availability_id:
        flash('Please select an available time slot.')
        return redirect(url_for('doctor.profile', doctor_id=doctor_id))
    
    # Get the availability slot
    availability = DoctorAvailability.query.get_or_404(availability_id)
    
    # Check if already booked
    if availability.is_booked:
        flash('This time slot has already been booked. Please choose another.')
        return redirect(url_for('doctor.profile', doctor_id=doctor_id))
    
    # Create appointment datetime from availability
    appointment_datetime = datetime.combine(availability.date, availability.start_time)
    
    new_appointment = Appointment(
        patient_id=patient.patient_id,
        doctor_id=doctor_id,
        datetime=appointment_datetime,
        status='confirmed',
        payment_method=payment_method
    )
    
    # Mark availability as booked
    availability.is_booked = True
    
    db.session.add(new_appointment)
    db.session.commit()
    
    flash('Appointment booked successfully!')
    return redirect(url_for('booking.dashboard'))

@booking_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    role = session.get('role')
    user_id = session.get('user_id')
    
    if role == 'patient':
        patient = Patient.query.filter_by(user_id=user_id).first()
        if not patient:
            flash('Patient profile not found.')
            return redirect(url_for('doctor.search'))
        appointments = Appointment.query.filter_by(patient_id=patient.patient_id).order_by(Appointment.datetime).all()
        return render_template('dashboard.html', appointments=appointments, role='patient')
        
    elif role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=user_id).first()
        if not doctor:
            flash('Doctor profile not found.')
            return redirect(url_for('doctor.search'))
        appointments = Appointment.query.filter_by(doctor_id=doctor.doctor_id).order_by(Appointment.datetime).all()
        availability_slots = DoctorAvailability.query.filter_by(doctor_id=doctor.doctor_id).order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()
        return render_template('dashboard.html', appointments=appointments, availability_slots=availability_slots, role='doctor', doctor=doctor)
        
    elif role == 'admin':
        unverified_doctors = Doctor.query.join(User).filter(User.verified == False, User.role == 'doctor').all()
        return render_template('dashboard.html', unverified_doctors=unverified_doctors, role='admin')
        
    return redirect(url_for('doctor.search'))

@booking_bp.route('/add_availability', methods=['POST'])
def add_availability():
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash('Only doctors can add availability.')
        return redirect(url_for('auth.login'))
    
    doctor = Doctor.query.filter_by(user_id=session['user_id']).first()
    
    if not doctor:
        flash('Doctor profile not found.')
        return redirect(url_for('booking.dashboard'))
    
    date_str = request.form.get('date')
    start_time_str = request.form.get('start_time')
    end_time_str = request.form.get('end_time')
    
    if not date_str or not start_time_str or not end_time_str:
        flash('All fields are required.')
        return redirect(url_for('booking.dashboard'))
    
    try:
        slot_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        start_time_obj = datetime.strptime(start_time_str, '%H:%M').time()
        end_time_obj = datetime.strptime(end_time_str, '%H:%M').time()
        
        # Check if slot already exists
        existing = DoctorAvailability.query.filter_by(
            doctor_id=doctor.doctor_id,
            date=slot_date,
            start_time=start_time_obj,
            end_time=end_time_obj
        ).first()
        
        if existing:
            flash('This availability slot already exists.')
            return redirect(url_for('booking.dashboard'))
        
        new_availability = DoctorAvailability(
            doctor_id=doctor.doctor_id,
            date=slot_date,
            start_time=start_time_obj,
            end_time=end_time_obj,
            is_booked=False
        )
        
        db.session.add(new_availability)
        db.session.commit()
        flash('Availability slot added successfully!')
    except Exception as e:
        flash(f'Error adding availability: {str(e)}')
    
    return redirect(url_for('booking.dashboard'))

@booking_bp.route('/delete_availability/<int:availability_id>', methods=['POST'])
def delete_availability(availability_id):
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash('Only doctors can delete availability.')
        return redirect(url_for('auth.login'))
    
    availability = DoctorAvailability.query.get_or_404(availability_id)
    
    # Check if already booked
    if availability.is_booked:
        flash('Cannot delete a booked slot.')
        return redirect(url_for('booking.dashboard'))
    
    db.session.delete(availability)
    db.session.commit()
    flash('Availability slot deleted.')
    return redirect(url_for('booking.dashboard'))

@booking_bp.route('/cancel/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    appointment = Appointment.query.get_or_404(appointment_id)
    
    # Free up the availability slot if it exists
    availability = DoctorAvailability.query.filter_by(
        doctor_id=appointment.doctor_id,
        date=appointment.datetime.date(),
        start_time=appointment.datetime.time()
    ).first()
    
    if availability:
        availability.is_booked = False
    
    appointment.status = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled.')
    return redirect(url_for('booking.dashboard'))

@booking_bp.route('/approve_doctor/<int:user_id>', methods=['POST'])
def approve_doctor(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
        
    user = User.query.get_or_404(user_id)
    user.verified = True
    db.session.commit()
    flash('Doctor approved.')
    return redirect(url_for('booking.dashboard'))
