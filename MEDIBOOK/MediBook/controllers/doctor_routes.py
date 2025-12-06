from flask import Blueprint, render_template, request
from models.user_model import Doctor, User
from models.appointment_model import Clinic, DoctorAvailability
from datetime import date

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/')
def search():
    specialization = request.args.get('specialization')
    location = request.args.get('location')
    
    query = Doctor.query.join(User).join(Clinic)
    
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
    
    if location:
        # Filter by city
        query = query.filter(Clinic.city.ilike(f'%{location}%'))
        
    doctors = query.all()
    
    # Get unique specializations for filter dropdown
    specializations = [s[0] for s in Doctor.query.with_entities(Doctor.specialization).distinct()]
    
    # Get unique cities for location filter
    cities = [c[0] for c in Clinic.query.with_entities(Clinic.city).distinct()]
    
    return render_template('home.html', doctors=doctors, specializations=specializations, cities=cities)

@doctor_bp.route('/doctor/<int:doctor_id>')
def profile(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Get available (not booked) slots for this doctor from today onwards
    today = date.today()
    available_slots = DoctorAvailability.query.filter_by(
        doctor_id=doctor_id,
        is_booked=False
    ).filter(DoctorAvailability.date >= today).order_by(
        DoctorAvailability.date,
        DoctorAvailability.start_time
    ).all()
    
    return render_template('doctor_profile.html', doctor=doctor, available_slots=available_slots)
