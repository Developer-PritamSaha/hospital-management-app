from flask import current_app as app
from .login_model import Doctor
from datetime import date, time, timedelta
from app_backend_Flask.application.db_extensions import db

class Availability(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False, index=True) 
    slot_id = db.Column(db.String(30), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    diagonisis_limit = db.Column(db.Integer, nullable=False, default=0)
    appointments_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.Boolean, nullable=False, default=False)

    @classmethod
    def create_default_availability(cls, doc_id: int):
        '''Creates default 7 days x 3 time slots into the database for the respective doctor else raises Exception'''

        doc = Doctor.query.filter_by(id=doc_id).first()
        if not doc:
            raise Exception("Doctor not found in the database to assign availability.")
        
        try:
            default_date = date(2026,1,5)
            default_time_slots = [(time(9, 0), time(12, 0)), (time(14, 0), time(17, 0)), (time(19, 0), time(22, 0)),]
            for i in range(0,7):
                for j in range(0,3):
                    new_slot = Availability(
                        doctor_id = doc_id,
                        slot_id = f"d{i+1}s{j+1}",
                        date = default_date + timedelta(days=i),
                        start_time = default_time_slots[j][0],
                        end_time = default_time_slots[j][1]
                    )

                    db.session.add(new_slot)
                    db.session.flush()

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Method) Availability.create_default_availability(): (triggered) default availability commit rollback: (cause) {e}")
            raise Exception(e)
        else:
            db.session.commit()

    @classmethod
    def check_status(cls, docId: int, slotId: str):
        '''Checks the doctor availability status for a time slot and returns the status'''
       
        doc_availability = Availability.query.filter_by(doctor_id=docId, slot_id=slotId).first()
       
        # Checks if the max patient appointment limit for status
        if (doc_availability.appointments_count < doc_availability.diagonisis_limit) and (doc_availability.status):
            return True
        else:
            return False 


class Department(db.Model):
    __tablename__ = 'department'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False, unique=True, index=True)
    description = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(30), nullable=False)

    @classmethod
    def create_default_departments(cls):
        '''Creates default departments into the database else raises Exception'''
        try:
            existing_dapartments_count = Department.query.count()

            if existing_dapartments_count < 20:
                new_department = Department(
                    name = "Emergency Care",
                    description = "The primary, 24/7 point of contact for immediate medical, accident, or trauma care.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "General Medicine",
                    description = "Manages non-surgical diseases and adult health.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "General Surgery",
                    description = "Performs routine operations, including appendectomies, hernia repairs, etc..",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Internal Medicine",
                    description = "Focused on the prevention, diagnosis, and treatment of complex diseases affecting internal organs, without surgery.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Obstetrics and Gynaecology",
                    description = "Manages pregnancy, childbirth, and female reproductive health.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Paediatrics",
                    description = "Specializes in the care of infants, children, and adolescents.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Orthopaedics",
                    description = "Treats injuries and diseases of the musculoskeletal system.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Intensive Care Unit (ICU)",
                    description = "Provides 24-hour monitoring for critically ill patients.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Anaesthesiology",
                    description = "Provides pain relief and sedation for surgeries.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Cardiology",
                    description = "Deals with diagnosis and treatment of heart and blood vessel disorders.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Neurology",
                    description = "Focuses on disorders of the brain, spinal cord, and nervous system.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Ophthalmology",
                    description = "Diagnoses and treats eye diseases and vision disorders.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "ENT (Otolaryngology)",
                    description = "Treats conditions related to ear, nose, throat, head, and neck.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Dermatology",
                    description = "Manages skin, hair, nail disorders, and cosmetic treatments.",
                    type = "normal"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Diagnostics",
                    description = "Supports clinical decisions through imaging and laboratory investigations.",
                    type = "normal"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Psychiatry & Mental Health",
                    description = "Provides diagnosis and treatment of mental and behavioral disorders.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Dental",
                    description = "Offers preventive and surgical care for oral and dental health.",
                    type = "normal"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Nephrology & Urology",
                    description = "Manages kidney, urinary tract, and male reproductive health.",
                    type = "essential"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Endocrinology",
                    description = "Focuses on hormone-related disorders and metabolic diseases.",
                    type = "normal"
                )
                db.session.add(new_department)
                db.session.flush()

                new_department = Department(
                    name = "Rehabilitation & Physiotherapy",
                    description = "Helps patients recover physical function after illness or injury.",
                    type = "normal"
                )
                db.session.add(new_department)
                db.session.flush()
            else:
                return None

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Method) Department.create_essential_departments(): (triggered) default departmets commit rollback: (cause) {e}")
            raise Exception(e)
        else:
            db.session.commit()

class Departments_Doctors(db.Model):
    __tablename__ = 'departments_doctors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id", ondelete="CASCADE"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("department.id"), nullable=False)

    @classmethod
    def dept_name(cls, docId: int):
        '''Returns the department_name of the doctor if exist else return "None"'''
        try:
            department_id = Departments_Doctors.query.filter_by(doctor_id=int(docId)).first().department_id
            department_name = Department.query.filter_by(id=department_id).first().name
        except Exception as e:
            app.logger.exception(f"(Method) Departments_Doctors.dept_name(): (cause) {e}")
            return(None)
        else:
            return str(department_name)
    
class Specialization(db.Model):
    __tablename__ = 'specialization'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(40), nullable=False, unique=True, index=True)

    @classmethod
    def create_default_specializations(cls):
        '''Creates default specialization into the database else raises Exception'''
        try:
            existing_specializations_count = Specialization.query.count()

            if existing_specializations_count < 48:
                new_specliztion = Specialization(
                    name = "General Physician",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Gastroenterology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Preventive Medicine",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Cardiology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Interventional Cardiology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Cardiac Electrophysiology",
                )
                db.session.add(new_specliztion)
                db.session.flush()
                                                        
                new_specliztion = Specialization(
                    name = "Neurology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Neurosurgery",
                )
                db.session.add(new_specliztion)
                db.session.flush()
                                                 
                new_specliztion = Specialization(
                    name = "Orthopedic Surgery",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Sports Medicine",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Joint Replacement",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "General Surgery",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Laparoscopic Surgery",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Minimally Invasive Surgery",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Pediatrics",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Neonatology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Pediatric Intensive Care",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Obstetrics",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Gynecology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Reproductive Medicine",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Ophthalmology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Cataract & Refractive Surgery",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "ENT",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Head & Neck Surgery",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Audiology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Dermatology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Cosmetology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Trichology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Radiology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Pathology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Hematology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Psychiatry",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Clinical Psychology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Child & Adolescent Psychiatry",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "General Dentistry",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Orthodontics",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Oral & Maxillofacial Surgery",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Emergency Medicine",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Trauma Care",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Pulmonology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Nephrology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Urology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Endocrinology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Diabetology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Physiotherapy",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Rehabilitation Medicine",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Anesthesiology",
                )
                db.session.add(new_specliztion)
                db.session.flush()

                new_specliztion = Specialization(
                    name = "Critical Care Medicine",
                )
                db.session.add(new_specliztion)
                db.session.flush()

            else:
                return None

        except Exception as e:
            db.session.rollback()
            app.logger.exception(f"(Method) Specialization.create_essential_specializations(): (triggered) default specializations commit rollback: (cause) {e}")
            raise Exception(e)
        else:
            db.session.commit()

    @classmethod
    def spec_name(cls, specId: int):
        '''Returns the specialization_name of the doctor if exist else return "None"'''
        try:
            spec_name = Specialization.query.filter_by(id=int(specId)).first().name
            
        except Exception as e:
            app.logger.exception(f"(Method) Specialization.spec_name(): (cause) {e}")
            return(None)
        else:
            return str(spec_name)