from ..extensions import db

class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id", ondelete="CASCADE"), nullable=False) 
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False) 
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    patient_treatment = db.relationship('Treatment', backref='appointment', cascade="all, delete-orphan")
    
class Treatment(db.Model):
    __tablename__ = 'treatment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id", ondelete="CASCADE"), nullable=False, unique=True)
    visit_type = db.Column(db.String(20), nullable=False)
    test_done = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    prescription = db.Column(db.Text, nullable=False)
    medicine = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=False)
