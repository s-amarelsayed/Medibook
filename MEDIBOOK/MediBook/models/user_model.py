from . import db

class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), unique=True)
    role = db.Column(db.Enum('patient', 'doctor', 'admin', name='user_roles'), default='patient', nullable=False)
    verified = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(255), default='default.png')

    # Relationships
    patient = db.relationship('Patient', backref='user', uselist=False)
    doctor = db.relationship('Doctor', backref='user', uselist=False)

class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20))

class Doctor(db.Model):
    __tablename__ = 'doctors'
    doctor_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id'), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)

    # Relationship to Clinic is defined in Appointment model or here? 
    # Usually defined where ForeignKey is.
    # Clinic model is in appointment_model.py, so we need to be careful with imports or string reference.
    # Using string reference 'Clinic' for relationship.
    clinic = db.relationship('Clinic', backref='doctors')
