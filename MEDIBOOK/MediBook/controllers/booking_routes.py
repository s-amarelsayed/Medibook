from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from repositories import UserRepository, AppointmentRepository, AvailabilityRepository, DoctorRepository, PatientRepository, ReviewRepository
from datetime import datetime

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book/<int:doctor_id>', methods=['POST'])
def book_appointment(doctor_id):
    if 'user_id' not in session or session.get('role') != 'patient':
        flash('Please login as a patient to book an appointment.')
        return redirect(url_for('auth.login'))

    doctor = DoctorRepository.get_by_id(doctor_id)
    if not doctor:
        flash('Doctor not found.')
        return redirect(url_for('doctor.search'))

    patient = PatientRepository.get_by_user_id(session['user_id'])
    if not patient:
        flash('Patient profile not found.')
        return redirect(url_for('doctor.profile', doctor_id=doctor_id))
    
    availability_id = request.form.get('availability_id')
    payment_method = 'at_clinic'
    
    if not availability_id:
        flash('Please select an available time slot.')
        return redirect(url_for('doctor.profile', doctor_id=doctor_id))
    
    availability = AvailabilityRepository.get_by_id(availability_id)
    if not availability or availability.is_booked:
        flash('This time slot is no longer available.')
        return redirect(url_for('doctor.profile', doctor_id=doctor_id))
    
    appointment_datetime = datetime.combine(availability.date, availability.start_time)
    
    AppointmentRepository.create(
        patient_id=patient.patient_id,
        doctor_id=doctor_id,
        datetime=appointment_datetime,
        status='confirmed',
        payment_method=payment_method
    )
    
    availability.is_booked = True
    UserRepository.commit()
    
    flash('Appointment booked successfully!')
    return redirect(url_for('booking.dashboard'))

@booking_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    role = session.get('role')
    user_id = session.get('user_id')
    
    if role == 'patient':
        patient = PatientRepository.get_by_user_id(user_id)
        if not patient:
            flash('Patient profile not found.')
            return redirect(url_for('doctor.search'))
        appointments = AppointmentRepository.get_by_patient(patient.patient_id)
        return render_template('dashboard.html', appointments=appointments, role='patient', now=datetime.now())
        
    elif role == 'doctor':
        doctor = DoctorRepository.get_by_user_id(user_id)
        if not doctor:
            flash('Doctor profile not found.')
            return redirect(url_for('doctor.search'))
        appointments = AppointmentRepository.get_by_doctor(doctor.doctor_id)
        availability_slots = AvailabilityRepository.get_by_doctor(doctor.doctor_id)
        
        # Add patient medical history to each appointment for doctor view
        for appt in appointments:
            if appt.patient and appt.patient.user and hasattr(appt.patient.user, 'patient') and appt.patient.user.patient:
                appt.patient_medical_history = appt.patient.user.patient.medical_history or 'Not provided'
            else:
                appt.patient_medical_history = 'Not provided'
        
        return render_template('dashboard.html', appointments=appointments, availability_slots=availability_slots, role='doctor', doctor=doctor)
        
    elif role == 'admin':
        unverified_doctors = DoctorRepository.get_unverified()
        return render_template('dashboard.html', unverified_doctors=unverified_doctors, role='admin')
        
    return redirect(url_for('doctor.search'))

@booking_bp.route('/add_availability', methods=['POST'])
def add_availability():
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash('Only doctors can add availability.')
        return redirect(url_for('auth.login'))
    
    doctor = DoctorRepository.get_by_user_id(session['user_id'])
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
        
        if AvailabilityRepository.get_existing(doctor.doctor_id, slot_date, start_time_obj, end_time_obj):
            flash('This availability slot already exists.')
            return redirect(url_for('booking.dashboard'))
        
        AvailabilityRepository.create(doctor.doctor_id, slot_date, start_time_obj, end_time_obj)
        UserRepository.commit()
        flash('Availability slot added successfully!')
    except Exception as e:
        flash(f'Error adding availability: {str(e)}')
    
    return redirect(url_for('booking.dashboard'))

@booking_bp.route('/delete_availability/<int:availability_id>', methods=['POST'])
def delete_availability(availability_id):
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash('Only doctors can delete availability.')
        return redirect(url_for('auth.login'))
    
    availability = AvailabilityRepository.get_by_id(availability_id)
    if not availability:
        flash('Availability slot not found.')
        return redirect(url_for('booking.dashboard'))
    
    if availability.is_booked:
        flash('Cannot delete a booked slot.')
        return redirect(url_for('booking.dashboard'))
    
    AvailabilityRepository.delete(availability)
    UserRepository.commit()
    flash('Availability slot deleted.')
    return redirect(url_for('booking.dashboard'))

@booking_bp.route('/cancel/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
        
    appointment = AppointmentRepository.get_by_id(appointment_id)
    if not appointment:
        flash('Appointment not found.')
        return redirect(url_for('booking.dashboard'))
    
    availability = AvailabilityRepository.get_existing(
        appointment.doctor_id,
        appointment.datetime.date(),
        appointment.datetime.time(),
        None # End time not needed for match in this context if using start_time+date
    )
    
    if availability:
        availability.is_booked = False
    
    appointment.status = 'cancelled'
    UserRepository.commit()
    flash('Appointment cancelled.')
    return redirect(url_for('booking.dashboard'))

@booking_bp.route('/submit_review/<int:appointment_id>', methods=['POST'])
def submit_review(appointment_id):
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect(url_for('auth.login'))
        
    appointment = AppointmentRepository.get_by_id(appointment_id)
    if not appointment:
        flash('Appointment not found.')
        return redirect(url_for('booking.dashboard'))
        
    patient = PatientRepository.get_by_user_id(session['user_id'])
    if not patient or appointment.patient_id != patient.patient_id:
        flash('Unauthorized access.')
        return redirect(url_for('booking.dashboard'))
        
    rating = request.form.get('rating')
    feedback = request.form.get('feedback')
    
    if not rating:
        flash('Rating is required.')
        return redirect(url_for('booking.dashboard'))
        
    ReviewRepository.create(
        patient_id=patient.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_id=appointment_id,
        rating=int(rating),
        feedback=feedback
    )
    UserRepository.commit()
    
    flash('Review submitted successfully!')
    return redirect(url_for('booking.dashboard'))