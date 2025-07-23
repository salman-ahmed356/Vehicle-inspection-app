from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from .database import db
from .enums import ReportStatus, Color, FuelType, TransmissionType

class Company(db.Model):
    __tablename__ = 'companies'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    address = Column(String(255))
    phone = Column(String(20))
    email = Column(String(100))
    website = Column(String(100))
    tax_number = Column(String(20))
    logo_path = Column(String(255))

class Customer(db.Model):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(100))
    tc_tax_number = Column(String(20))
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    id = Column(Integer, primary_key=True)
    plate = Column(String(20), nullable=False)
    brand = Column(String(50), nullable=False)
    model = Column(String(50), nullable=False)
    chassis_number = Column(String(50), unique=True, nullable=False)
    engine_number = Column(String(50))
    color = Column(Enum(Color), nullable=False)
    model_year = Column(Integer, nullable=False)
    transmission_type = Column(Enum(TransmissionType), nullable=False)
    fuel_type = Column(Enum(FuelType), nullable=False)
    mileage = Column(Integer)
    
    # Relationships
    reports = relationship("Report", back_populates="vehicle")
    owner = relationship("VehicleOwner", back_populates="vehicle", uselist=False)

class VehicleOwner(db.Model):
    __tablename__ = 'vehicle_owners'
    id = Column(Integer, primary_key=True)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="owner")
    customer = relationship("Customer")

class Staff(db.Model):
    __tablename__ = 'staff'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(20))
    role = Column(String(50))
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Package(db.Model):
    __tablename__ = 'packages'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Float)
    
    # Relationships
    package_expertises = relationship("PackageExpertise", back_populates="package")

class ExpertiseType(db.Model):
    __tablename__ = 'expertise_types'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('expertise_types.id'))
    
    # Relationships
    children = relationship("ExpertiseType", 
                           backref=db.backref('parent', remote_side=[id]))
    expertise_reports = relationship("ExpertiseReport", back_populates="expertise_type")

class PackageExpertise(db.Model):
    __tablename__ = 'package_expertises'
    id = Column(Integer, primary_key=True)
    package_id = Column(Integer, ForeignKey('packages.id'), nullable=False)
    expertise_type_id = Column(Integer, ForeignKey('expertise_types.id'), nullable=False)
    
    # Relationships
    package = relationship("Package", back_populates="package_expertises")
    expertise_type = relationship("ExpertiseType")

class Report(db.Model):
    __tablename__ = 'reports'
    id = Column(Integer, primary_key=True)
    inspection_date = Column(DateTime, default=datetime.utcnow)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    package_id = Column(Integer, ForeignKey('packages.id'), nullable=False)
    operation = Column(String(255))
    created_by = Column(Integer, ForeignKey('staff.id'))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    registration_document_seen = Column(Boolean, default=False)
    status = Column(Enum(ReportStatus), default=ReportStatus.OPENED)
    
    # Relationships
    vehicle = relationship("Vehicle", back_populates="reports")
    customer = relationship("Customer")
    package = relationship("Package")
    staff = relationship("Staff")
    expertise_reports = relationship("ExpertiseReport", back_populates="report")
    
    def get_expertise_report(self, expertise_type_name):
        for er in self.expertise_reports:
            if er.expertise_type and er.expertise_type.name == expertise_type_name:
                return er
        return None

class Agent(db.Model):
    __tablename__ = 'agents'
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('reports.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    
    # Relationships
    report = relationship("Report")
    customer = relationship("Customer")

class ExpertiseReport(db.Model):
    __tablename__ = 'expertise_reports'
    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('reports.id'), nullable=False)
    expertise_type_id = Column(Integer, ForeignKey('expertise_types.id'), nullable=False)
    comment = Column(Text)
    front_na = Column(Boolean, default=False)
    rear_na = Column(Boolean, default=False)
    park_na = Column(Boolean, default=False)
    
    # Relationships
    report = relationship("Report", back_populates="expertise_reports")
    expertise_type = relationship("ExpertiseType", back_populates="expertise_reports")
    features = relationship("ExpertiseFeature", back_populates="expertise_report")

class ExpertiseFeature(db.Model):
    __tablename__ = 'expertise_features'
    id = Column(Integer, primary_key=True)
    expertise_report_id = Column(Integer, ForeignKey('expertise_reports.id'), nullable=False)
    name = Column(String(100), nullable=False)
    status = Column(String(100))
    image_path = Column(String(255))
    
    # Relationships
    expertise_report = relationship("ExpertiseReport", back_populates="features")