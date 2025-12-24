from . import db

class Clinic(db.Model):
    __tablename__ = 'clinics'
    clinic_id = db.Column(db.Integer, primary_key=True)
    #phase5: Custom clinic locations
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))

class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum('pending', 'confirmed', 'cancelled', name='appointment_status'), default='pending')
    payment_method = db.Column(db.Enum('online', 'at_clinic', name='payment_methods'), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    # Relationships
    patient = db.relationship('Patient', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

class DoctorAvailability(db.Model):
    __tablename__ = 'doctor_availability'
    availability_id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False)
    
    # Relationship
    doctor = db.relationship('Doctor', backref='availability_slots')

class Review(db.Model):
    #phase5: Review system
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.appointment_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    # Relationships
    patient = db.relationship('Patient', backref='reviews')
    doctor = db.relationship('Doctor', backref='reviews')
    appointment = db.relationship('Appointment', backref='review', uselist=False)
