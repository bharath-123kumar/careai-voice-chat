import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

Base = declarative_base()

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    specialty = Column(String)

class Appointment(Base):
    __tablename__ = "appointments"
    id = Column(Integer, primary_key=True)
    patient_id = Column(String)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String) # booked, cancelled, completed

class AppointmentEngine:
    def __init__(self, db_url="sqlite:///./appointments.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_doctors(self, specialty=None):
        session = self.Session()
        query = session.query(Doctor)
        if specialty:
            query = query.filter(Doctor.specialty.contains(specialty))
        doctors = query.all()
        session.close()
        return doctors

    def check_availability(self, doctor_id, start_time):
        session = self.Session()
        # Assume 30 min appointments
        end_time = start_time + datetime.timedelta(minutes=30)
        
        # Check for overlaps
        conflict = session.query(Appointment).filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == "booked",
            Appointment.start_time < end_time,
            Appointment.end_time > start_time
        ).first()
        
        session.close()
        return conflict is None

    def book_appointment(self, patient_id, doctor_id, start_time):
        if not self.check_availability(doctor_id, start_time):
            return {"success": False, "message": "Slot already booked."}
        
        if start_time < datetime.datetime.now():
            return {"success": False, "message": "Cannot book in the past."}

        session = self.Session()
        end_time = start_time + datetime.timedelta(minutes=30)
        new_app = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            start_time=start_time,
            end_time=end_time,
            status="booked"
        )
        session.add(new_app)
        session.commit()
        app_id = new_app.id
        session.close()
        return {"success": True, "appointment_id": app_id}

    def cancel_appointment(self, appointment_id):
        session = self.Session()
        app = session.query(Appointment).filter(Appointment.id == appointment_id).first()
        if app:
            app.status = "cancelled"
            session.commit()
            session.close()
            return {"success": True}
        session.close()
        return {"success": False, "message": "Appointment not found."}

    def seed_data(self):
        session = self.Session()
        if session.query(Doctor).count() == 0:
            doctors = [
                Doctor(name="Dr. Sharma", specialty="Cardiologist"),
                Doctor(name="Dr. Priya", specialty="Dermatologist"),
                Doctor(name="Dr. Tamil", specialty="General Physician")
            ]
            session.add_all(doctors)
            session.commit()
        session.close()
