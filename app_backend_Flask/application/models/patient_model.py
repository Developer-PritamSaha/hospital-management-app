from app_backend_Flask.application.db_extensions import db
from app_backend_Flask.application.utils.generate_credentials_uid import generate_uuid

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id", ondelete="CASCADE"), nullable=False, index=True) 
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False, index=True) 
    public_id = db.Column(db.String(20), nullable=False, unique=True, index=True, default=lambda: generate_uuid("AP"))
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='booked') ## Other Values : 'canceled' or 'completed'
    patient_treatment = db.relationship('Treatment', backref='appointment', cascade="all, delete-orphan")
    
class Treatment(db.Model):
    __tablename__ = 'treatment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    visit_type = db.Column(db.String(20), nullable=False)
    test_done = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=False)
    medicine = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=False)
