"""
Repository Pattern Implementation
Isolates all database queries in a dedicated layer
"""

from models.user_model import User, Patient, Doctor
from models.appointment_model import Clinic, Appointment, DoctorAvailability, Review
from database_singleton import db_singleton


class UserRepository:
    """Repository for User-related database operations"""
    
    @staticmethod
    def commit():
        db_singleton.session.commit()

    @staticmethod
    def rollback():
        db_singleton.session.rollback()

    @staticmethod
    def flush():
        db_singleton.session.flush()

    @staticmethod
    def get_by_id(user_id):
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_email(email):
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def create(name, email, password_hash, role, verified=False, profile_picture='default.png'):
        """Factory method to create and persist a new User."""
        user = User(name=name, email=email, password_hash=password_hash, role=role, verified=verified, profile_picture=profile_picture)
        db_singleton.session.add(user)
        return user
    
    @staticmethod
    def get_all():
        return User.query.all()

    @staticmethod
    def create_patient(user_id, dob, phone):
        patient = Patient(user_id=user_id, dob=dob, phone=phone)
        db_singleton.session.add(patient)
        return patient

    @staticmethod
    def create_doctor(user_id, clinic_id, specialization, price, bio=''):
        doctor = Doctor(user_id=user_id, clinic_id=clinic_id, specialization=specialization, price=price, bio=bio)
        db_singleton.session.add(doctor)
        return doctor


class DoctorRepository:
    """Repository for Doctor-related database operations"""
    
    @staticmethod
    def get_by_id(doctor_id):
        return Doctor.query.get(doctor_id)
    
    @staticmethod
    def get_by_user_id(user_id):
        return Doctor.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def get_unverified():
        return Doctor.query.join(User).filter(User.verified == False, User.role == 'doctor').all()
    
    @staticmethod
    def search(specialization=None, city=None, name=None):
        query = Doctor.query.join(User).join(Clinic)
        if specialization:
            query = query.filter(Doctor.specialization.ilike(f'%{specialization}%'))
        if city:
            query = query.filter(Clinic.city.ilike(f'%{city}%'))
        if name:
            query = query.filter(User.name.ilike(f'%{name}%'))
        return query.all()
    
    @staticmethod
    def get_specializations():
        return [s[0] for s in Doctor.query.with_entities(Doctor.specialization).distinct()]

    @staticmethod
    def count():
        return Doctor.query.count()


class PatientRepository:
    """Repository for Patient-related database operations"""
    
    @staticmethod
    def get_by_user_id(user_id):
        return Patient.query.filter_by(user_id=user_id).first()

    @staticmethod
    def count():
        return Patient.query.count()


class ClinicRepository:
    """Repository for Clinic-related database operations"""
    
    @staticmethod
    def get_all():
        return Clinic.query.all()
    @staticmethod
    def get_cities():
        return [c[0] for c in Clinic.query.with_entities(Clinic.city).distinct()]

    @staticmethod
    def create(name, address, city, country, phone):
        clinic = Clinic(name=name, address=address, city=city, country=country, phone=phone)
        db_singleton.session.add(clinic)
        return clinic


class AppointmentRepository:
    """Repository for Appointment-related database operations"""
    
    @staticmethod
    def get_by_patient(patient_id):
        return Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.created_at.desc()).all()
    
    @staticmethod
    def get_by_doctor(doctor_id):
        return Appointment.query.filter_by(doctor_id=doctor_id).order_by(Appointment.datetime).all()

    @staticmethod
    def get_by_id(appointment_id):
        return Appointment.query.get(appointment_id)

    @staticmethod
    def create(patient_id, doctor_id, datetime, status='confirmed', payment_method='at_clinic'):
        """Factory method to create and persist a new Appointment."""
        appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id, datetime=datetime, status=status, payment_method=payment_method)
        db_singleton.session.add(appointment)
        return appointment

    @staticmethod
    def count():
        return Appointment.query.count()


class AvailabilityRepository:
    """Repository for Doctor Availability operations"""
    
    @staticmethod
    def get_available_slots(doctor_id, from_date):
        return DoctorAvailability.query.filter_by(doctor_id=doctor_id, is_booked=False).filter(
            DoctorAvailability.date >= from_date
        ).order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()

    @staticmethod
    def get_by_doctor(doctor_id):
        return DoctorAvailability.query.filter_by(doctor_id=doctor_id).order_by(DoctorAvailability.date, DoctorAvailability.start_time).all()

    @staticmethod
    def get_by_id(availability_id):
        return DoctorAvailability.query.get(availability_id)

    @staticmethod
    def get_existing(doctor_id, date, start_time, end_time=None):
        query = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=date,
            start_time=start_time
        )
        if end_time:
            query = query.filter_by(end_time=end_time)
        return query.first()

    @staticmethod
    def create(doctor_id, date, start_time, end_time, is_booked=False):
        availability = DoctorAvailability(doctor_id=doctor_id, date=date, start_time=start_time, end_time=end_time, is_booked=is_booked)
        db_singleton.session.add(availability)
        return availability

    @staticmethod
    def delete(availability):
        db_singleton.session.delete(availability)


class ReviewRepository:
    """Repository for Review operations"""
    
    @staticmethod
    def get_by_doctor(doctor_id):
        return Review.query.filter_by(doctor_id=doctor_id).order_by(Review.created_at.desc()).all()

    @staticmethod
    def create(patient_id, doctor_id, appointment_id, rating, feedback):
        review = Review(patient_id=patient_id, doctor_id=doctor_id, appointment_id=appointment_id, rating=rating, feedback=feedback)
        db_singleton.session.add(review)
        return review
