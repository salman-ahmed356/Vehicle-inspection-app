from datetime import datetime

from ..database import db
from ..enums import (
    ReportStatus,
    Color,
    TransmissionType,
    FuelType
)


class Address(db.Model):
    __tablename__ = 'address'
    id = db.Column(db.Integer, primary_key=True)
    street_address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=True)
    postal_code = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f'<Address {self.street_address}, {self.city}, {self.state}>'


class Agent(db.Model):
    __tablename__ = 'agent'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)

    __table_args__ = {'extend_existing': True}

    def __repr__(self):
        return f'<Agent {self.first_name} {self.last_name}>'


class Appointment(db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    brand = db.Column(db.String(50), nullable=True)
    model = db.Column(db.String(50), nullable=True)
    reminder_sent = db.Column(db.Boolean, default=False)

    customer = db.relationship('Customer', backref='appointments', lazy=True)

    def __repr__(self):
        return f'<Appointment {self.brand} - {self.date} {self.time}>'


class Branch(db.Model):
    __tablename__ = 'branch'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False, index=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=True, index=True)

    address = db.relationship('Address', backref='branches', lazy=True)
    staff_members = db.relationship('Staff', backref='branch', lazy=True)

    def __repr__(self):
        return f'<Branch {self.name}>'


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    fax = db.Column(db.String(15))
    email = db.Column(db.String(100))
    website = db.Column(db.String(100))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=True)
    # my_business_address_link field removed temporarily

    address = db.relationship('Address', backref='companies', lazy=True)
    branches = db.relationship('Branch', backref='company', lazy=True)

    def __repr__(self):
        return f'<Company {self.name}>'


class Customer(db.Model):
    __tablename__ = 'customer'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    tc_tax_number = db.Column(db.String(11), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=True)

    address = db.relationship('Address', backref='customers', lazy=True)
    reports = db.relationship('Report', back_populates='customer', lazy=True, overlaps="customer_reports,customer")
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<Customer {self.first_name} {self.last_name}>'


class ExpertiseType(db.Model):
    __tablename__ = 'expertise_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('expertise_types.id'), nullable=True, index=True)

    expertise_reports = db.relationship('ExpertiseReport', back_populates='expertise_type', lazy=True)
    children = db.relationship('ExpertiseType', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def __repr__(self):
        return f'<ExpertiseType {self.name}>'


class ExpertiseReport(db.Model):
    __tablename__ = 'expertise_reports'
    __table_args__ = {'extend_existing': True}

    id                = db.Column(db.Integer, primary_key=True)
    report_id         = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False, index=True)
    expertise_type_id = db.Column(db.Integer, db.ForeignKey('expertise_types.id'), nullable=False, index=True)
    comment           = db.Column(db.Text, nullable=True)

    # ← Matching two-way relationship
    report = db.relationship(
        'Report',
        back_populates='expertise_reports',
        lazy=True
    )

    expertise_type = db.relationship(
        'ExpertiseType',
        back_populates='expertise_reports',
        lazy=True
    )
    features = db.relationship(
        'ExpertiseFeature',
        back_populates='expertise_report',
        cascade="save-update, merge",
        lazy=True
    )

    def __repr__(self):
        return f'<ExpertiseReport {self.expertise_type.name}>'




class ExpertiseFeature(db.Model):
    __tablename__ = 'expertise_features'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    expertise_report_id = db.Column(db.Integer, db.ForeignKey('expertise_reports.id'), nullable=False, index=True)

    expertise_report = db.relationship('ExpertiseReport', back_populates='features', lazy=True)

    def __repr__(self):
        return f'<ExpertiseFeature {self.name} - {self.status}>'


class PackageExpertise(db.Model):
    __tablename__ = 'package_expertises'
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False, index=True)
    expertise_type_id = db.Column(db.Integer, db.ForeignKey('expertise_types.id'), nullable=False, index=True)

    package = db.relationship('Package', back_populates='package_expertises', lazy=True)
    expertise_type = db.relationship('ExpertiseType', lazy=True)

    def __repr__(self):
        return f'<PackageExpertise {self.package.name} - {self.expertise_type.name}>'


class Package(db.Model):
    __tablename__ = 'package'
    id     = db.Column(db.Integer, primary_key=True)
    name   = db.Column(db.String(50), nullable=False)
    price  = db.Column(db.Float,   nullable=False)
    active = db.Column(db.Boolean, default=True)

    reports = db.relationship(
        'Report',
        back_populates='package',
        lazy=True
    )

    package_expertises = db.relationship(
        'PackageExpertise',
        back_populates='package',
        cascade="all, delete-orphan",
        lazy=True
    )

    package_contents = db.relationship(
        'PackageContent',
        back_populates='package',
        cascade="all, delete-orphan",
        lazy=True
    )

    def __repr__(self):
        return f'<Package {self.name}>'

    @property
    def expertises(self):
        """
        Returns a list of expertise-type names linked to this package.
        Allows your template to do: {% for name in package.expertises %}.
        """
        return [
            pe.expertise_type.name
            for pe in self.package_expertises
        ]



class PackageContent(db.Model):
    __tablename__ = 'package_content'
    __table_args__ = (
        db.UniqueConstraint('package_id', 'content_item',
                            name='uq_package_content_item'),
    )

    id           = db.Column(db.Integer, primary_key=True)
    package_id   = db.Column(db.Integer, db.ForeignKey('package.id'),
                             nullable=False)
    content_item = db.Column(db.String(100), nullable=False)

    # remove backref, use back_populates instead
    package = db.relationship('Package',
                              back_populates='package_contents',
                              lazy=True)

    def __repr__(self):
        return f'<PackageContent {self.content_item}>'



from datetime import datetime


from datetime import datetime
from ..database import db
from ..enums import ReportStatus

class Report(db.Model):
    __tablename__   = 'report'
    __table_args__  = {'extend_existing': True}

    id                         = db.Column(db.Integer, primary_key=True)
    inspection_date            = db.Column(db.DateTime, nullable=False)
    vehicle_id                 = db.Column(db.Integer, db.ForeignKey('vehicle.id'),   nullable=False, index=True)
    customer_id                = db.Column(db.Integer, db.ForeignKey('customer.id'),  nullable=False, index=True)
    package_id                 = db.Column(db.Integer, db.ForeignKey('package.id'),   nullable=False, index=True)
    operation                  = db.Column(db.String(255))
    created_at                 = db.Column(db.DateTime, default=datetime.utcnow)
    created_by                 = db.Column(db.Integer, db.ForeignKey('staff.id'),     nullable=False, index=True)
    registration_document_seen = db.Column(db.Boolean, nullable=False)
    status                     = db.Column(db.Enum(ReportStatus), default=ReportStatus.OPENED, nullable=False)
    has_image                  = db.Column(db.Boolean, default=False)
    image_data                 = db.Column(db.LargeBinary, nullable=True)

    customer = db.relationship(
        'Customer',
        back_populates='reports',
        lazy=True,
        overlaps="customer_reports,customer"
    )
    package = db.relationship(
        'Package',
        back_populates='reports',
        lazy=True
    )
    staff = db.relationship(
        'Staff',
        back_populates='reports_created',
        lazy=True,
        overlaps="staff_reports,staff"
    )
    vehicle = db.relationship(
        'Vehicle',
        back_populates='reports',
        lazy=True
    )

    # ← Add this relationship to link back from ExpertiseReport
    expertise_reports = db.relationship(
        'ExpertiseReport',
        back_populates='report',
        lazy=True
    )
    
    # Add vehicle_owner relationship like customer
    vehicle_owner = db.relationship(
        'VehicleOwner',
        back_populates='report',
        uselist=False,
        lazy=True
    )

    def __repr__(self):
        return f'<Report {self.id}>'

    def get_expertise_report(self, expertise_type_name: str):
        """
        Returns the ExpertiseReport for this report & expertise type,
        or None if no record exists.
        """
        # Delay import to avoid circularity
        from .all_models import ExpertiseType

        et = ExpertiseType.query.filter_by(name=expertise_type_name).first()
        if not et:
            return None

        # Search the in-memory list rather than re-querying
        return next(
            (er for er in self.expertise_reports if er.expertise_type_id == et.id),
            None
        )



class Staff(db.Model):
    __tablename__ = 'staff'

    id           = db.Column(db.Integer,   primary_key=True)
    first_name   = db.Column(db.String(50), nullable=False)
    last_name    = db.Column(db.String(50), nullable=False)
    password     = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15),  nullable=False)
    department   = db.Column(db.String(50),  nullable=True)
    role         = db.Column(db.String(50),  nullable=False)

    branch_id = db.Column(
        db.Integer,
        db.ForeignKey('branch.id'),
        nullable=True,
        index=True
    )
    reports_created = db.relationship(
        'Report',
        back_populates='staff',
        lazy=True,
        overlaps='staff_reports,staff'
    )

    def __repr__(self):
        return f'<Staff {self.first_name} {self.last_name} - {self.role}>'

    @property
    def full_name(self):
        """
        Returns the staff member’s full name by joining first and last.
        Used by forms, templates, etc., wherever you called staff.full_name.
        """
        return f"{self.first_name} {self.last_name}"



from sqlalchemy.orm import validates


class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.Integer, primary_key=True)
    plate = db.Column(db.String(10), nullable=False, unique=True)
    engine_number = db.Column(db.String(17), nullable=True, unique=True)
    brand = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    chassis_number = db.Column(db.String(17), nullable=False, unique=True)
    color = db.Column(db.Enum(Color), nullable=False)
    model_year = db.Column(db.Integer, nullable=False)
    transmission_type = db.Column(db.Enum(TransmissionType), nullable=False)
    fuel_type = db.Column(db.Enum(FuelType), nullable=False)
    mileage = db.Column(db.Integer, nullable=False)

    reports = db.relationship('Report', back_populates='vehicle', lazy=True)

    @validates('model_year')
    def validate_model_year(self, key, value):
        current_year = datetime.now().year
        if value < 1950 or value > current_year:
            raise ValueError(f'Model year must be between 1950 and {current_year}.')
        return value

    def __repr__(self):
        return f'<Vehicle {self.plate} - {self.brand} {self.model}>'


class VehicleOwner(db.Model):
    __tablename__ = 'vehicle_owner'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    tc_tax_number = db.Column(db.String(11), nullable=True, index=True)
    phone_number = db.Column(db.String(15), nullable=False, index=True)
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=True, index=True)
    report_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)

    address = db.relationship('Address', backref='vehicle_owners', lazy=True)
    report = db.relationship('Report', back_populates='vehicle_owner', lazy=True)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f'<VehicleOwner {self.first_name} {self.last_name}>'
