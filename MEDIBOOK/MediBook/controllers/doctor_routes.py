from flask import Blueprint, render_template, request
from repositories import DoctorRepository, ClinicRepository, AvailabilityRepository, ReviewRepository
from datetime import date

doctor_bp = Blueprint('doctor', __name__)

@doctor_bp.route('/')
def search():
    specialization = request.args.get('specialization')
    location = request.args.get('location')
    name_query = request.args.get('name')
    
    doctors = DoctorRepository.search(specialization=specialization, city=location, name=name_query)
    
    # Get unique specializations for filter dropdown
    specializations = DoctorRepository.get_specializations()
    
    # Get unique cities for location filter
    cities = ClinicRepository.get_cities()
    
    return render_template('home.html', doctors=doctors, specializations=specializations, cities=cities)

@doctor_bp.route('/doctor/<int:doctor_id>')
def profile(doctor_id):
    doctor = DoctorRepository.get_by_id(doctor_id)
    if not doctor:
        from flask import abort
        abort(404)
    
    # Get available (not booked) slots for this doctor from today onwards
    today = date.today()
    available_slots = AvailabilityRepository.get_available_slots(doctor_id, today)
    
    # Fetch reviews for the doctor
    reviews = ReviewRepository.get_by_doctor(doctor_id)
    
    return render_template('doctor_profile.html', doctor=doctor, available_slots=available_slots, reviews=reviews)
